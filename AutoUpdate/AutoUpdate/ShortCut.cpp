#include "ShortCut.h"
#include <Windows.h>
#include <shlobj.h>
#include <string>

ShortCut::ShortCut(void)
{
}

ShortCut::~ShortCut(void)
{
}

std::wstring ShortCut::str2wstr(std::string s) {
	std::wstring ws;
	ws.assign(s.begin(), s.end());
	return ws;
}

void ShortCut::CreateShortcut(std::string source, std::string workingDirectory, std::string target) {
	// inspiration taken from: http://www.cplusplus.com/forum/windows/28812/
	CoInitialize(NULL);
    IShellLink* pShellLink = NULL;
    HRESULT hres;
    hres = CoCreateInstance(CLSID_ShellLink, NULL, CLSCTX_ALL,
                   IID_IShellLink, (void**)&pShellLink);
    if (SUCCEEDED(hres))
    {		
		pShellLink->SetPath(str2wstr(source).c_str());  // Path to the object we are referring to
		pShellLink->SetWorkingDirectory(str2wstr(workingDirectory).c_str());
        pShellLink->SetDescription(L"The Digital Panda");
        pShellLink->SetIconLocation(str2wstr(source).c_str(), 0);
    
        IPersistFile *pPersistFile;
        hres = pShellLink->QueryInterface(IID_IPersistFile, (void**)&pPersistFile);
        
        if (SUCCEEDED(hres))
        {
			hres = pPersistFile->Save(str2wstr(target).c_str(), TRUE);
            pPersistFile->Release();
        }
        else
        {
            throw std::string("error");
        }
        pShellLink->Release();
    }
    else
    {
		throw std::string("error");
    }
}
