#include "Process.h"
#include <stdio.h>
#include <stdlib.h>
#include <process.h>
#include <boost/filesystem.hpp>
#include <string>
#include <direct.h>

void Process::Run(std::string &location) {
	using namespace std;
	boost::filesystem::path p(location);
	string arg0 = p.filename().string();
	// start the application in the directory it's installed
	_chdir(p.parent_path().string().c_str());
	_spawnl(_P_NOWAIT, location.c_str(), arg0.c_str(), NULL);
}
