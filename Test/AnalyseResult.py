# coding=utf-8
from __builtin__ import range
import ftplib
import socket

__author__ = 'Michael'

import os

#FTP服务器IP地址
FTP_HOST = '10.129.41.70'
#FTP用户名
FTP_USER_NAME = 'imetest'
#FTP密码
FTP_PASSWD = 'Sogou7882Imeqa'
#下载到本地进行分析的文件
LOCAL_RESULT_FILE = '../Result/result.txt'
#FTP文件路径
REMOTE_FILE_PATH = '/WordCrawler'
#分析结果文件
ANALYSE_FILE_PATH = '../Result/analyse_result.txt'


class ImeInfo:
    VersionName = ""
    VersionCode = ""
    PackageName = ""


class report:
    imeInfo = ImeInfo()
    #总个数
    totalCount = 0
    #首选命中个数
    firstHitCount = 0
    #首屏未命中个数
    missCount = 0
    #首屏命中个数
    hitNotFirstCount = 0
    #Log校验结果
    isCorrect = False

    def downloadFile(self):
        if (os.path.isfile(LOCAL_RESULT_FILE) and os.path.exists(LOCAL_RESULT_FILE)):
            os.remove(LOCAL_RESULT_FILE)
        try:
            f = ftplib.FTP(FTP_HOST)
        except (socket.error, socket.gaierror), e:
            return False

        try:
            f.login(user=FTP_USER_NAME, passwd=FTP_PASSWD)
        except ftplib.error_perm:
            print 'FTP login failed!\r\n'
            f.quit()
            return False
        print 'Login success!\r\n'

        try:
            dir_list = []
            f.dir(dir_list.append)
            f.retrbinary('RETR %s' % self.getLatestFileOnFtp(f), open(LOCAL_RESULT_FILE, 'wb').write)
        except ftplib.error_perm:
            print 'Cannot read remote file!\r\n'
            os.unlink(REMOTE_FILE_PATH)
            return False
        else:
            print 'Download file complete!\r\n'
            return True

    def getLatestFileOnFtp(self, ftp):
        files = []
        try:
            ftp.cwd('/WordCrawler/')
            files = ftp.nlst()
        except ftplib.error_perm, resp:
            if str(resp) == "550 No files found":
                print "no files in this directory"
            else:
                raise

        return files[files.__len__() - 1]

    def record(self, oneResult):
        if oneResult == '' or oneResult is None:
            return

        self.totalCount += 1

        lines = oneResult.split('\n')
        for line in lines:
            if line.startswith('target'):
                if line.startswith('target:1'):
                    self.firstHitCount += 1
                elif line.startswith('target:0'):
                    self.missCount += 1
                else:
                    self.hitNotFirstCount += 1

        return

    def analyse(self):
        oneResult = ''
        resultFile = open(LOCAL_RESULT_FILE, 'r')
        for line in resultFile:
            line = line.decode('UTF-8')
            if line.startswith('wordstart'):
                oneResult = ''
            elif line.startswith('wordend'):
                self.record(oneResult)
            else:
                oneResult += line

    def getImeInfo(self):
        resultFile = open(LOCAL_RESULT_FILE, 'r')
        for i in range(0, 3):
            line = resultFile.readline()
            if line.startswith('IMEName'):
                self.imeInfo.PackageName = line[line.index(':') + 1:]
            elif line.startswith('IMEVersionName'):
                self.imeInfo.VersionName = line[line.index(':') + 1:]
            elif line.startswith('IMEVersionCode'):
                self.imeInfo.VersionCode = line[line.index(':') + 1:]

        return


    def checkLog(self):
        if self.totalCount == self.firstHitCount + self.hitNotFirstCount + self.missCount:
            return True
        else:
            return False

    def writeAnalyseResult(self):
        analyseFile = open(ANALYSE_FILE_PATH, 'w')
        target = ['case总数: ' + str(self.totalCount) + '\n', '首选命中数： ' + str(self.firstHitCount) + '\n',
                  '首选命中率： ' + str((self.firstHitCount * 1.000) / self.totalCount) + '\n',
                  '首屏命中数： ' + str(self.totalCount - self.missCount) + '\n',
                  '首屏命中率： ' + str(((self.totalCount - self.missCount) * 1.000) / self.totalCount) + '\n',
                  '输入法名称: ' + self.imeInfo.PackageName, '输入法Version Name： ' + self.imeInfo.VersionName,
                  '输入法Version Code： ' + self.imeInfo.VersionCode, 'Log文件校验结果: ' + '正确' if self.isCorrect else '错误']
        #target = target.encode("UTF-8")
        analyseFile.writelines(target)
        return


    def main(self):
        if self.downloadFile():
            self.getImeInfo()
            self.analyse()

        self.isCorrect = self.checkLog()

        self.writeAnalyseResult()


if __name__ == '__main__':
    reporter = report()
    reporter.main()