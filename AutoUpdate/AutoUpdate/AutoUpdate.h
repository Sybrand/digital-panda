#pragma once
#include "ApplicationVersion.h"
#include "HttpResponse.h"
#include <string>

namespace panda {
	using namespace std;

	class AutoUpdate
	{
	private:
		std::string applicationSubFolder;
		std::string applicationVersionStream;
		std::string applicationVersionHost;
		std::string endl;
		std::string userAgent;

		std::string GetApplicationPath();
		std::string GetPandaPath();
		std::string GetShortcutPath();

		ApplicationVersion GetAvailableVersion();

		bool IsInstalled();

		bool DownloadUpdate(ApplicationVersion &);
		bool UpdateAvailable();

		bool InstallUpdate(ApplicationVersion &);

		bool RunPanda();

		bool IsFileOk(std::string &, std::string &);

		std::string GetUpdatePath(ApplicationVersion &);
		void GetCurrentVersion(std::string &version, std::string &location);
		std::string AutoUpdate::GetExecutablePath();
		std::string GetCurrentVersionPath();

	public:
		AutoUpdate(void) {
			// TODO: load from config
			applicationVersionHost = "www.digitalpanda.co.za";
			applicationSubFolder = "Digital Panda";
			applicationVersionStream = "/updates_dev/win7_32.txt";
			endl = "\r\n";
			userAgent = "Digital Panda";
		}
		~AutoUpdate(void);
		void CheckForUpdateAndRun(void);
	};

}