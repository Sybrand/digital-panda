#include "Compression.h"
#include <unzip.h>

#include <string>
#include <boost/filesystem.hpp>
#include <fstream>
#include <boost/date_time/posix_time/posix_time.hpp>

#define MAX_FILE_LENGTH  1024
#define READ_SIZE 8096

using namespace boost::posix_time;
using namespace boost::gregorian;

Compression::Compression(void)
{

}

Compression::~Compression(void)
{
}

void Compression::Unzip(std::string &sourceFile, std::string &sTargetPath) {
	using namespace std;
	// zip is a nightmare
	// inspiration taken from : http://stackoverflow.com/questions/10440113/simple-way-to-unzip-a-zip-file-using-zlib
	unzFile f = unzOpen(sourceFile.c_str());
	if (!f) {
		unzClose(f);
		throw new string("could not open");
	}
	unz_global_info global_info;
	if (unzGetGlobalInfo(f, &global_info)!=UNZ_OK) {
		unzClose(f);
		throw new string("could not get global info");
	}
	char fileName[MAX_FILE_LENGTH];
	char buff[READ_SIZE];
	unz_file_info fileInfo;
	for (uLong i = 0; i < global_info.number_entry; ++i ) {
		if (unzGetCurrentFileInfo(f, &fileInfo, fileName, MAX_FILE_LENGTH, NULL, 0, NULL, 0) != UNZ_OK) {
			unzClose(f);
			throw new string("could not read file info");
		}
		const size_t fileNameLen = strlen(fileName);
		boost::filesystem::path tmpPath(sTargetPath);
		tmpPath /= fileName;
		if (fileName[fileNameLen-1]=='/') {
			// make directory
			if (!boost::filesystem::exists(tmpPath)) {
				// create directory if it doesn't exist
				if (!boost::filesystem::create_directory(tmpPath)) {
					unzCloseCurrentFile(f);
					unzClose(f);
					throw new string("could not create directory");
				}
			}
		} else {
			// uncompress file
			if (unzOpenCurrentFile(f) != UNZ_OK) {
				unzCloseCurrentFile(f);
				unzClose(f);
				throw new string("could not open current file");
			}
			ofstream of;
			// we truncate whatever might be there
			of.open(tmpPath.string(), ios::out | ios::binary | ios::trunc);
			if (!of.is_open()) {
				unzCloseCurrentFile(f);
				unzClose(f);
				throw new string("could not open file");
			}
			int error = UNZ_OK;
			do {
				error = unzReadCurrentFile(f, buff, READ_SIZE);
				if (error<0) {
					unzCloseCurrentFile(f);
					unzClose(f);
					throw new string("unzip error");
				}
				if (error>0) {
					of.write(buff, error);
				}
			} while (error>0);
			of.flush();
			of.close();
		}
		// set the date of the file/directory to match that of the zip
		SetFileTime(tmpPath, fileInfo);
		// close the current entry in the zip
		unzCloseCurrentFile( f );
		// move to next entry in zip
		if (i+1< global_info.number_entry) {
			if ( unzGoToNextFile( f ) != UNZ_OK ) {
				unzClose(f);
				throw new string("could not go to next file");
			}
		}
	}
	unzClose(f);
}

void Compression::SetFileTime(boost::filesystem::path &filePath, unz_file_info &fileInfo) {
	// create gregorian date
	date d(fileInfo.tmu_date.tm_year, 
		fileInfo.tmu_date.tm_mon+1, 
		fileInfo.tmu_date.tm_mday);
	// create posix time
	ptime pt(d);
	// create epoch
	ptime epoch(date(1970,1,1));
	// count seconds passed since epoch
	time_duration::sec_type s = (pt-epoch).total_seconds() + 
		fileInfo.tmu_date.tm_hour*60*60 + 
		fileInfo.tmu_date.tm_min*60 + 
		fileInfo.tmu_date.tm_sec;
	// crate time from seconds
	time_t t(s);
	// grand - but we need the time in term of the local time
	std::tm *lt = std::localtime(&t);
	// set the file time (finally!)
	boost::filesystem::last_write_time(filePath, mktime(lt));
}
