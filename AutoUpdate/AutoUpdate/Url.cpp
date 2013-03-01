#include "Url.h"
#include <string>
#include <sstream>

Url::Url(void)
{
}


Url::~Url(void)
{
}

bool Url::isHexDigit(char c) {
	const std::string hexDigit = "0123456789ABCDEF";
	return hexDigit.find_first_of(c)!=std::string::npos;
}

bool Url::HtmlIsReserved(char c) {
	// http://tools.ietf.org/html/rfc3986 says these are unreserved:
	const std::string unreserved = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_.~";
	return unreserved.find_first_of(c)==std::string::npos;
}

std::string Url::urlEncode(std::string &s) {
	using namespace std;
	// used for inspiration: http://codepad.org/lCypTglt
	stringstream escaped;
	for (size_t i=0;i<s.length();++i) {
		// we don't escape / (might change this later to be optional?)
		if (HtmlIsReserved(s[i]) && s[i]!='/') {
			escaped << "%" << std::hex << (int)s[i];
		} else {
			escaped << s[i];
		}
	}
	return escaped.str();
}

std::string Url::urlDecode(std::string &s) {
	using namespace std;
	stringstream unescaped;
	for (size_t i=0;i<s.length();++i) {
		if (s[i]=='%' && i+2<s.length() && isHexDigit(s[i+1]) && isHexDigit(s[i+2])) {
			stringstream ss;
			ss << std::hex << s.substr(i+2, 2);
			unescaped << ss.str();
		} else {
			unescaped << s[i];
		}
	}
	return unescaped.str();
}
