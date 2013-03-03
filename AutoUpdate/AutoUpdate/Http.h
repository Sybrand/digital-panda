#pragma once
#include "HttpResponse.h"
#include <string>
#include <stdint.h>
#include <boost/asio/ip/tcp.hpp>

class Http
{
private:
	std::string endl;
	uintmax_t GetFileResumePosition(std::string &);
public:
	bool Download(std::string &host, std::string &protocol, std::string &source, std::string &target, unsigned long int fileSize, std::string &hash);
	// TODO: make this private
	static HttpResponse GetResponse(boost::asio::ip::tcp::iostream &);
	Http(void);
	~Http(void);
};

