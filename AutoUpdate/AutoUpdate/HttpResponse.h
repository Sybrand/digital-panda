#pragma once
#include <string>

class HttpResponse
{
public:
	std::string http_version;
	unsigned int status_code;
	std::string status_message;

	HttpResponse(void);
	~HttpResponse(void);
};

