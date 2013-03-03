#pragma once
#include <string>
#include <boost/filesystem.hpp>
#include <unzip.h>

class Compression
{
private:
	void SetFileTime(boost::filesystem::path &, unz_file_info &);
public:
	Compression();
	~Compression(void);
	void Unzip(std::string &, std::string &);
};

