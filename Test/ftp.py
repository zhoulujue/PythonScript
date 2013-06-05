__author__ = 'Michael'
import ftplib

ftp = ftplib.FTP("10.129.41.70")
ftp.login("imetest", "Sogou7882Imeqa")

# data = []
#
# ftp.dir(data.append)
#
# ftp.quit()
#
# for line in data:
#     print "-", line

def getLatestFileOnFtp(ftp):
    files = []
    try:
        ftp.cwd('/WordCrawler/')
        files = ftp.nlst()
    except ftplib.error_perm, resp:
        if str(resp) == "550 No files found":
            print "no files in this directory"
        else:
            raise

    return files[files.__len__()-1]

print getLatestFileOnFtp(ftp)