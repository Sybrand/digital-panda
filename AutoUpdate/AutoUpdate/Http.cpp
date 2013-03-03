#include "Http.h"
#include "Url.h"
#include <boost/filesystem.hpp>
#include <hl_md5wrapper.h>
#include <boost/asio.hpp>
#include <boost/asio/ip/tcp.hpp>


Http::Http(void)
{
	endl = "\r\n";
}


Http::~Http(void)
{
}


uintmax_t Http::GetFileResumePosition(std::string &filePath) {
		if (boost::filesystem::exists(filePath)) {
			return boost::filesystem::file_size(filePath);
		}
		return 0;
	}

HttpResponse Http::GetResponse(boost::asio::ip::tcp::iostream &stream) {
	HttpResponse httpResponse;
	stream >> httpResponse.http_version;
	stream >> httpResponse.status_code;
	std::getline(stream, httpResponse.status_message);
		
	std::string header;
	while (std::getline(stream, header) && header != "\r") {
		std::cout << header << "\n";
	}
	return httpResponse;
}

bool Http::Download(std::string &host, std::string &protocol, std::string &source, std::string &target, unsigned long int fileSize, std::string &hash) {
	intmax_t previousPosition = -1;
	intmax_t resumePosition = GetFileResumePosition(target);
	if (resumePosition>fileSize) {
		//  larger than expected??? the start from the begin please!
		resumePosition = 0;
	}
	while (resumePosition>previousPosition && resumePosition<fileSize) {
		previousPosition = resumePosition;
		//totalBytesRead = resumePosition;
		// download it
		boost::asio::ip::tcp::iostream stream;
		stream.expires_from_now(boost::posix_time::seconds(60));
		stream.connect(host, protocol);
		if (!stream) {
			throw std::string("can't connect");
		}
		stream << "GET " << Url::urlEncode(source) << " HTTP/1.1" << endl;
		stream << "Host: " << host << endl;
		stream << "Accept: */*" << endl;
		stream << "User-Agent: " << "Digital Panda" << endl;
		stream << "Range: bytes=" << resumePosition << "-" << fileSize << endl;
		stream << "Connection: close" << endl << endl;
		stream.flush();
		// get request response
		HttpResponse response = GetResponse(stream);
		if (!(response.status_code==200 || response.status_code==206)) {
			throw response.status_message;
		}

		boost::filesystem::path path(target);
		if (!boost::filesystem::exists(path.parent_path())) {
			// create directory if it doesn't exist
			if (!boost::filesystem::create_directory(path.parent_path())) {
				throw std::string("failed to create directory");
			}
		}
		// write the file
		std::ofstream updateFile;
		if (resumePosition>0) {
			// we are resuming - so we append
			updateFile.open(target, std::ios::out | std::ios::binary | std::ios::app);
		} else {
			// we aren't resuming, so we start from 0/overwrite
			updateFile.open(target, std::ios::out | std::ios::binary | std::ios::trunc);
		}
		if (!updateFile.is_open()) {
			throw std::string("failed to open!");
		}
					
		while (stream.rdbuf()->available()>0) {
			updateFile << stream.rdbuf();
		}
			
		updateFile.flush();
		updateFile.close();

		if (boost::filesystem::file_size(target)==fileSize) {
			// compare the hash
			md5wrapper md5;
			return hash == md5.getHashFromFile(target);
		}
		// if we got this far - it means we're trying for another round
		resumePosition = GetFileResumePosition(target);
	}
	return false;
}
