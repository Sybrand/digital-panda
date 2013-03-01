#pragma once
#include "ApplicationVersion.h"
#include "HttpResponse.h"
#include <string>
#include <boost/asio/ip/tcp.hpp>

namespace panda {
	using namespace std;
	using namespace boost::asio;

	class AutoUpdate
	{
	private:
		std::string applicationSubFolder;
		std::string applicationVersionStream;
		std::string applicationVersionHost;
		std::string endl;
		std::string userAgent;

		std::string GetApplicationPath();

		ApplicationVersion GetAvailableVersion();

		bool IsInstalled() {
			// is the application installed?
			string applicationFolder = GetApplicationPath();
			return false;
		}

		bool DownloadUpdate(ApplicationVersion &);
		bool UpdateAvailable();

		bool InstallUpdate(ApplicationVersion &);

		bool RunApplication();

		HttpResponse GetResponse(boost::asio::ip::tcp::iostream &);

		std::string GetUpdatePath(ApplicationVersion &);

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