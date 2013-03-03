#include "AutoUpdate.h"
#include "ApplicationVersion.h"
#include "Url.h"
#include "Compression.h"
#include "Http.h"
#include <stdlib.h> // getenv
#include <sstream>
#include <fstream>
#include <hl_md5wrapper.h>
// from: http://stackoverflow.com/questions/2629421/how-to-use-boost-in-visual-studio-2010
// 1) you need to download boost
// 2) you need to change to not using pre-compiled headers, and set boost as additional directory
// 3) from visual studio command line, run bootstrap.bat
// 4) Run b2: (Win32) b2 --toolset=msvc-10.0 --build-type=complete stage ; (x64) b2 --toolset=msvc-10.0 --build-type=complete architecture=x86 address-model=64 stage
#include <boost/filesystem.hpp>
#include <boost/asio.hpp>
#include <boost/asio/ip/tcp.hpp>

namespace panda {

	AutoUpdate::~AutoUpdate(void)
	{
	}

	void AutoUpdate::CheckForUpdateAndRun(void) {
		if (IsInstalled()) {
			if (UpdateAvailable()) {
				ApplicationVersion version = GetAvailableVersion();
				if (DownloadUpdate(version)) {
					if (!InstallUpdate(version)) {
						// TODO: handle this
					}
				} else { // download failed
					// TODO: handle this
				}
			} else { // no update available
				// TODO: handle this!
			}
			if (!RunApplication()) {
				// TODO: handle this
			}
		} else { // not installed
			// get the latest version location
			ApplicationVersion version = GetAvailableVersion();
			if (DownloadUpdate(version)) {
				if (InstallUpdate(version)) {
					if (!RunApplication()) {
						// TODO: handle this
					}
				} else { // failed to install update
					// TODO: handle this
				}
			}
		}
	}

	std::string AutoUpdate::GetApplicationPath() {
		char *pValue;
		size_t len;
		std::stringstream ss;
		errno_t err = _dupenv_s( &pValue, &len, "APPDATA" );	
		if (err) {
			throw string("failed to get env. variable");
		};
		// pValue is null terminated - so we don't read the last byte
		ss.write(pValue, len-1);		
		free(pValue);
		ss << "\\" << applicationSubFolder;
		return ss.str();
	}

	bool AutoUpdate::RunApplication() {
		return false;
	}

	bool AutoUpdate::InstallUpdate(ApplicationVersion &version) {
		string updatePath = GetUpdatePath(version);

		string applicationPath = GetApplicationPath();
		
		Compression compress;
		compress.Unzip(updatePath, applicationPath);

		return true;
	}

	bool AutoUpdate::UpdateAvailable() {
		return false;
	}

	std::string AutoUpdate::GetUpdatePath(ApplicationVersion &version) {
		string applicationPath = GetApplicationPath();
		boost::filesystem::path tmpPath(version.location);
		std::stringstream ss;
		ss << applicationPath << "\\updates\\" << tmpPath.filename().string();
		return ss.str();
	}

	bool AutoUpdate::IsFileOk(std::string &filePath, std::string &expectedHash) {
		if (boost::filesystem::exists(filePath)) {
			// wooah - it already exists? sweet!
			// check the md5 to confirm
			md5wrapper md5;
			string hash = md5.getHashFromFile(filePath);
			if (hash == expectedHash) {
				return true;
			}
		}
		return false;
	}

	bool AutoUpdate::DownloadUpdate(ApplicationVersion &version) {
		
		// look if we don't maybe already have the file
		// decide where we're downloading this file to
		
		std::string filePath = GetUpdatePath(version);
		if (IsFileOk(filePath, version.hash)) {
			return true;
		}
		Http http;
		return http.Download(version.host, version.protocol, version.location, filePath, version.fileSize, version.hash);
	}

	ApplicationVersion AutoUpdate::GetAvailableVersion() {
		ApplicationVersion applicationVersion;
			
		boost::asio::ip::tcp::iostream stream;
		stream.expires_from_now(boost::posix_time::seconds(60));
		stream.connect(applicationVersionHost, "http");
		if (!stream)
		{
			throw std::string("can't connect");
		}
		stream << "GET " << applicationVersionStream << " HTTP/1.0" << endl;
		stream << "Host: " << applicationVersionHost << endl;
		stream << "Accept: */*" << endl;
		stream << "User-Agent: " << userAgent << endl;
		stream << "Connection: close" << endl << endl;
		stream.flush();

		HttpResponse response = Http::GetResponse(stream);

		if (response.status_code != 200) {
			throw response.status_message;
		}
		std::getline(stream, applicationVersion.version);
		std::getline(stream, applicationVersion.protocol);
		std::getline(stream, applicationVersion.host);
		std::getline(stream, applicationVersion.location);
		std::getline(stream, applicationVersion.hash);
		std::string fileSize;
		std::getline(stream, fileSize);
		istringstream(fileSize) >> applicationVersion.fileSize;
		return applicationVersion;
	}

}