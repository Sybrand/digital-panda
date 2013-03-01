#pragma once
#include <string>

class Html
{
private:
	static bool isHexDigit(char c);
	static bool HtmlIsReserved(char c);
public:
	static std::string urlEncode(std::string &);
	static std::string urlDecode(std::string &);
	Html(void);
	~Html(void);
};

