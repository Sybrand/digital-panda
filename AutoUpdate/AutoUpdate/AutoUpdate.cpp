#include "AutoUpdate.h"
#include <stdlib.h> // getenv
#include <sstream>
// from: http://stackoverflow.com/questions/2629421/how-to-use-boost-in-visual-studio-2010
// 1) you need to download boost
// 2) you need to change to not using pre-compiled headers, and set boost as additional directory
// 3) from visual studio command line, run bootstrap.bat
// 4) b2 --toolset=msvc-10.0 --build-type=complete stage ; (x64) b2 --toolset=msvc-10.0 --build-type=complete architecture=x86 address-model=64 stage


#include <boost/asio.hpp>

using namespace std;

AutoUpdate::AutoUpdate(void)
{
	// TODO: load from config
	applicationSubFolder = "Digital Panda";
}


AutoUpdate::~AutoUpdate(void)
{
}

std::string AutoUpdate::GetAvailableVersion() {
	boost::asio::ip::tcp::iostream stream("www.boost.org", "http");
	if (!stream)
	{
	  // Can't connect.
	}
	return NULL;
}

string AutoUpdate::GetApplicationPath() {
	//char *appdata = getenv("APPDATA");
	char *pValue;
	size_t len;
	std::stringstream ss;
	errno_t err = _dupenv_s( &pValue, &len, "APPDATA" );	
	if (err) {
		throw string("failed to get env. variable");
	};
	ss << *pValue << "\\" << applicationSubFolder;
	free(pValue);
	return ss.str();
}

bool AutoUpdate::IsInstalled() {
	// is the application installed?
	string applicationFolder = GetApplicationPath();

	return false;
}

void AutoUpdate::CheckForUpdateAndRun(void) {
	if (IsInstalled()) {
		if (UpdateAvailable()) {
			if (DownloadUpdate()) {
				if (!InstallUpdate()) {
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
		if (DownloadUpdate()) {
			if (InstallUpdate()) {
				if (!RunApplication()) {
					// TODO: handle this
				}
			} else { // failed to install update
				// TODO: handle this
			}
		}
	}
}

bool AutoUpdate::RunApplication() {
	return false;
}

bool AutoUpdate::InstallUpdate() {
	return false;
}

bool AutoUpdate::UpdateAvailable() {
	return false;
}

bool AutoUpdate::DownloadUpdate() {
	return false;
}