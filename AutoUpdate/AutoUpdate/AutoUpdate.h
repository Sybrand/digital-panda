#pragma once
#include <string>

class AutoUpdate
{
private:
	std::string applicationSubFolder;
	std::string GetApplicationPath();
	std::string GetAvailableVersion();
	bool IsInstalled();
	bool DownloadUpdate();
	bool UpdateAvailable();
	bool InstallUpdate();
	bool RunApplication();
public:
	AutoUpdate(void);
	~AutoUpdate(void);
	void CheckForUpdateAndRun(void);
};

