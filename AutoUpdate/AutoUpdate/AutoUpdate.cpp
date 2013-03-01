#include "AutoUpdate.h"
#include "ApplicationVersion.h"
#include "Url.h"
#include <stdlib.h> // getenv
#include <sstream>
#include <fstream>
#include <hl_md5wrapper.h>
// from: http://stackoverflow.com/questions/2629421/how-to-use-boost-in-visual-studio-2010
// 1) you need to download boost
// 2) you need to change to not using pre-compiled headers, and set boost as additional directory
// 3) from visual studio command line, run bootstrap.bat
// 4) Run b2: (Win32) b2 --toolset=msvc-10.0 --build-type=complete stage ; (x64) b2 --toolset=msvc-10.0 --build-type=complete architecture=x86 address-model=64 stage
#include <boost/asio/ip/tcp.hpp>
#include <boost/filesystem.hpp>
#include <zzip/zzip.h>

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
		ZZIP_DIR* dir = zzip_dir_open(updatePath.c_str(), 0);
		if (dir) {
			ZZIP_DIRENT dirent;
			while (zzip_dir_read(dir, &dirent)) {
				ZZIP_FILE* fp = zzip_file_open(dir, dirent.d_name, 0);
				if (fp) {

				}
				else {
					break;
				}
			}
		}
		zzip_dir_close(dir);
		// zip is a nightmare - we can use boost to gunzip
		// http://www.boost.org/doc/libs/1_41_0/libs/iostreams/doc/classes/gzip.html#examples

		// we can untar using --- ???

		return false;
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

	bool AutoUpdate::DownloadUpdate(ApplicationVersion &version) {
		// look if we don't maybe already have the file
		// decide where we're downloading this file to
		std::string filePath = GetUpdatePath(version);
		if (boost::filesystem::exists(filePath)) {
			// wooah - it already exists? sweet!
			// check the md5 to confirm
			md5wrapper md5;
			string hash = md5.getHashFromFile(filePath);
			if (hash == version.hash) {
				return true;
			}
		}
		// download it
		ip::tcp::iostream stream;
		stream.expires_from_now(boost::posix_time::seconds(60));
		stream.connect(version.host, version.protocol);
		if (!stream) {
			throw std::string("can't connect");
		}
		stream << "GET " << Url::urlEncode(version.location) << " HTTP/1.0" << endl;
		stream << "Host: " << version.host << endl;
		stream << "Accept: */*" << endl;
		stream << "User-Agent: " << userAgent << endl;
		stream << "Connection: close" << endl << endl;
		stream.flush();
		// get request response
		HttpResponse response = GetResponse(stream);
		if (response.status_code != 200) {
			throw response.status_message;
		}
		
		boost::filesystem::path path(filePath);
		if (!boost::filesystem::exists(path.parent_path())) {
			// create directory if it doesn't exist
			if (!boost::filesystem::create_directory(path.parent_path())) {
				throw std::string("failed to create directory");
			}
		}
		// write the file
		std::ofstream updateFile;
		updateFile.open(filePath, ios::out | ios::binary);
		if (!updateFile.is_open()) {
			throw std::string("failed to open!");
		}
		updateFile << stream.rdbuf();
		updateFile.flush();
		updateFile.close();
		// compare the hash
		md5wrapper md5;
		string hash = md5.getHashFromFile(filePath);

		return hash == version.hash;
	}

	ApplicationVersion AutoUpdate::GetAvailableVersion() {
		ApplicationVersion applicationVersion;
			
		ip::tcp::iostream stream;
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
		stream << "Connection: close" << endl << endl;;
		stream.flush();

		HttpResponse response = GetResponse(stream);

		if (response.status_code != 200) {
			throw response.status_message;
		}
		std::getline(stream, applicationVersion.version);
		std::getline(stream, applicationVersion.protocol);
		std::getline(stream, applicationVersion.host);
		std::getline(stream, applicationVersion.location);
		std::getline(stream, applicationVersion.hash);
		return applicationVersion;
	}

	HttpResponse AutoUpdate::GetResponse(boost::asio::ip::tcp::iostream &stream) {
		HttpResponse httpResponse;
		stream >> httpResponse.http_version;
		stream >> httpResponse.status_code;
		std::getline(stream, httpResponse.status_message);
		
		std::string header;
		while (std::getline(stream, header) && header != "\r") {
			std::cout << header << "\n";
		}
		return httpResponse;
	}

}