#include "AutoUpdate.h"
#include "ApplicationVersion.h"
#include "Url.h"
#include "Compression.h"
#include "Http.h"
#include "Process.h"
#include "ShortCut.h"
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

	void AutoUpdate::GetCurrentVersion(std::string &version, std::string &location) {
		string versionPath = GetCurrentVersionPath();
		ifstream is;
		is.open(versionPath, ios::in);
		std::getline(is, version);
		std::getline(is, location);
		is.close();
	}

	std::string AutoUpdate::GetPandaPath() {
		string currentVersion;
		string currentLocation;
		GetCurrentVersion(currentVersion, currentLocation);
		boost::filesystem::path applicationFolder(GetApplicationPath());
		applicationFolder /= currentLocation;
		applicationFolder /= "panda-tray-w.exe";
		return applicationFolder.string();
	}

	std::string AutoUpdate::GetShortcutPath() {
		boost::filesystem::path applicationFolder(GetApplicationPath());
		applicationFolder /= "Digital Panda.lnk";
		return applicationFolder.string();
	}

	bool AutoUpdate::IsInstalled() {
		// do we have a version path?
		string versionPath = GetCurrentVersionPath();
		if (boost::filesystem::exists(versionPath)) {
			// is the application installed?
			string applicationPath = GetPandaPath();
			return boost::filesystem::exists(applicationPath);
		}
		return false;
	}

	void AutoUpdate::CheckForUpdateAndRun(void) {
		// TODO: differentiate between running from link - or not
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
			if (!RunPanda()) {
				// TODO: handle this
			}
		} else { // not installed
			// get the latest version location
			ApplicationVersion version = GetAvailableVersion();
			if (DownloadUpdate(version)) {
				if (InstallUpdate(version)) {
					if (!RunPanda()) {
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

	bool AutoUpdate::RunPanda() {
		Process p;
		p.Run(GetPandaPath());
		return true;
	}

	bool AutoUpdate::InstallUpdate(ApplicationVersion &version) {
		string updatePath = GetUpdatePath(version);

		string applicationPath = GetApplicationPath();
		
		boost::filesystem::path tmpPath(updatePath);
		stringstream targetPath;
		string fileName = tmpPath.filename().string();
		string::size_type pos = fileName.find_last_of('.');
		string directoryName = fileName.substr(0, pos==string::npos? fileName.length()-1 : pos);
		targetPath << applicationPath << "\\" << directoryName;
		// make sure the targetpath exists
		if (!boost::filesystem::exists(targetPath.str())) {
			boost::filesystem::create_directory(targetPath.str());
		}
		
		Compression compress;
		// unzip update to the target path
		compress.Unzip(updatePath, targetPath.str());
		// write application version to disk
		
		ofstream of;
		of.open(AutoUpdate::GetCurrentVersionPath(), ios::out | ios::trunc);
		of << version.GetVersion() << std::endl;
		of << directoryName << std::endl;
		of.flush();
		of.close();


		std::string sPandaPath = GetPandaPath();
		boost::filesystem::path pandaPath(sPandaPath);
		ShortCut sc;
		sc.CreateShortcut(sPandaPath, pandaPath.parent_path().string(), GetShortcutPath());

		return true;
	}

	std::string AutoUpdate::GetCurrentVersionPath() {
		string applicationPath = GetApplicationPath();
		boost::filesystem::path versionPath;
		versionPath /= applicationPath;
		versionPath /= "version.txt";
		return versionPath.string();
	}

	bool AutoUpdate::UpdateAvailable() {
		string currentVersion;
		string currentLocation;
		GetCurrentVersion(currentVersion, currentLocation);

		ApplicationVersion availableVersion = GetAvailableVersion();
		
		double dCurrentVersion;
		double dAvailableVersion;
		istringstream(availableVersion.GetVersion()) >> dAvailableVersion;
		istringstream(currentVersion) >> dCurrentVersion;
		return dAvailableVersion > dCurrentVersion;
	}

	std::string AutoUpdate::GetUpdatePath(ApplicationVersion &version) {
		string applicationPath = GetApplicationPath();
		boost::filesystem::path tmpPath(version.GetLocation());
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
		if (IsFileOk(filePath, version.GetHash())) {
			return true;
		}
		Http http;
		return http.Download(version.GetHost(), version.GetProtocol(), version.GetLocation(), filePath, version.GetFileSize(), version.GetHash());
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
		std::string strTmp;
		std::getline(stream, strTmp);
		applicationVersion.SetVersion(strTmp);
		std::getline(stream, strTmp);
		applicationVersion.SetProtocol(strTmp);
		std::getline(stream, strTmp);
		applicationVersion.SetHost(strTmp);
		std::getline(stream, strTmp);
		applicationVersion.SetLocation(strTmp);
		std::getline(stream, strTmp);
		applicationVersion.SetHash(strTmp);
		std::string fileSize;
		std::getline(stream, fileSize);
		unsigned long int ulFileSize;
		istringstream(fileSize) >> ulFileSize;
		applicationVersion.SetFileSize(ulFileSize);
		return applicationVersion;
	}

}