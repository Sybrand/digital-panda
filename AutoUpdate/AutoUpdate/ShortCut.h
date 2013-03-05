#pragma once
#include <string>

class ShortCut
{
private:
	std::wstring ShortCut::str2wstr(std::string s);
public:
	ShortCut(void);
	~ShortCut(void);
	void CreateShortcut(std::string source, std::string workingDirectory, std::string target);
};

