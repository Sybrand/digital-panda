#pragma once

#include <string>

class ApplicationVersion
{
private:
	
public:
	std::string version;
	std::string protocol;
	std::string host;
	std::string location;
	std::string hash;
	/*
	void setVersion(std::string version) {
		this->version = version;
	}
	void setLocation(std::string location) {
		this->location = location;
	}
	*/
};
