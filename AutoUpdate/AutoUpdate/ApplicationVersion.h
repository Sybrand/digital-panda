#pragma once

#include <string>

class ApplicationVersion
{
private:
	std::string Trim(std::string &s) {
		using namespace std;
		string::size_type pos1 = s.find_first_not_of(' ');
		string::size_type pos2 = s.find_last_not_of(' ');
		return s.substr(pos1==string::npos ? 0 : pos1,
			pos2==string::npos ? s.length()-1 : pos2-pos1+1);
	}
	std::string version;
	std::string protocol;
	std::string host;
	std::string location;
	std::string hash;
	unsigned long int fileSize;
public:
	void SetVersion(std::string &version) {
		this->version = Trim(version);
	}
	std::string GetVersion() {
		return this->version;
	}
	void SetProtocol(std::string &protocol) {
		this->protocol = Trim(protocol);
	}
	std::string GetProtocol() {
		return this->protocol;
	}
	void SetHost(std::string &host) {
		this->host = Trim(host);
	}
	std::string GetHost() {
		return this->host;
	}
	void SetLocation(std::string &location) {
		this->location = Trim(location);
	}
	std::string GetLocation() {
		return this->location;
	}
	void SetHash(std::string &hash) {
		this->hash = Trim(hash);
	}
	std::string GetHash() {
		return this->hash;
	}
	void SetFileSize(unsigned long int fileSize) {
		this->fileSize = fileSize;
	}
	unsigned long int GetFileSize() {
		return this->fileSize;
	}
};

