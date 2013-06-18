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
#下载到本地进行分析的result文件
LOCAL_RESULT_FILE = '../Result/result.txt'
#下载到本地进行分析的raw.config文件
LOCAL_CONFIG_FILE = '../Result/raw.config'
#FTP文件路径
REMOTE_FILE_PATH = '/WordCrawler'
#raw.config文件路径
REMOTE_CONFIG_PATH = '/WordCrawler/raw.config'
#分析结果文件
ANALYSE_FILE_PATH = '../Result/analyse_result.txt'


class ImeInfo:
    VersionName = ""
    VersionCode = ""
    PackageName = ""


class report:
    imeInfo = ImeInfo()
    mRawConfig = None
    #总个数
    mTotalCount = 0
    #权重总和
    mTotalWeight = 0
    #首选命中个数
    mFirstHitCount = 0
    #首选命中权重
    mFirstHitWeight = 0
    #首屏未命中个数
    mMissCount = 0
    #首屏未命中权重
    mMissWeight = 0
    #首屏命中个数
    mHitNotFirstCount = 0
    #首屏命中权重
    mHitNotFirstWeight = 0
    #Log校验结果
    mIsCorrect = False

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
            f.retrbinary('RETR %s' % self.getLatestFileOnFtp(f), open(LOCAL_RESULT_FILE, 'wb').write)
            f.retrbinary('RETR %s' % REMOTE_CONFIG_PATH, open(LOCAL_CONFIG_FILE, 'wb').write)
        except ftplib.error_perm:
            print 'Cannot read remote file!\r\n'
            #os.unlink(REMOTE_FILE_PATH)
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
        self.mTotalCount += 1
        lines = oneResult.split('\n')
        weightStr = "error"
        try:
            weightStr = self.getCaseWeight(self.mRawConfig, lines[0][7:])
            weight = int(weightStr)
        except ValueError:
            print weightStr + ", error in convert weight!"
            print lines[0]
            weight = 0

        self.mTotalWeight += weight

        for line in lines:
            if line.__contains__('target'):
                if line.__contains__('target:1'):
                    self.mFirstHitCount += 1
                    self.mFirstHitWeight += weight
                elif line.__contains__('target:0'):
                    self.mMissCount += 1
                    self.mMissWeight += weight
                else:
                    self.mHitNotFirstCount += 1
                    self.mHitNotFirstWeight += weight

        return

    def analyse(self):
        oneResult = ''
        resultFile = open(LOCAL_RESULT_FILE, 'r')
        for line in resultFile:
            line = line.decode('UTF-8')
            if line.__contains__('wordstart'):
                oneResult = ''
            elif line.__contains__('wordend'):
                self.record(oneResult)
            else:
                oneResult += line

    def getImeInfo(self):
        resultFile = open(LOCAL_RESULT_FILE, 'r')
        for i in range(0, 10):
            line = resultFile.readline()
            if line.__contains__('IMEName'):
                self.imeInfo.PackageName = line[line.index(':') + 1:line.__len__() - 1]
            elif line.__contains__('IMEVersionName'):
                self.imeInfo.VersionName = line[line.index(':') + 1:line.__len__() - 1]
            elif line.__contains__('IMEVersionCode'):
                self.imeInfo.VersionCode = line[line.index(':') + 1:line.__len__() - 1]

        return

    def getCaseWeight(self, rawConfig, inputStr):
        line = ""
        line = rawConfig.readline()
        pinyin = inputStr[:inputStr.index('\t')]
        pinyin = pinyin.encode()
        if line.find(pinyin) != -1:
            lines = line.split(',')
            weights = lines[lines.__len__() - 1].split("\"")
            return weights[weights.__len__() - 2]
        else:
            print inputStr + ', error in reading weight!'
            return "0"

    def checkLog(self):
        if self.mTotalCount == self.mFirstHitCount + self.mHitNotFirstCount + self.mMissCount:
            print '个数校验成功！'
            if self.mTotalWeight == self.mFirstHitWeight + self.mHitNotFirstWeight + self.mMissWeight:
                print '权重校验成功！'
                return True
        else:
            return False

    def writeAnalyseResult(self):
        analyseFile = open(ANALYSE_FILE_PATH, 'w')
        target = ['case总数: ' + str(self.mTotalCount) + '\n',
                  '首选命中数： ' + str(self.mFirstHitCount) + '\n',
                  '首选命中率(带权重): ' + str((self.mFirstHitWeight * 1.000) / self.mTotalWeight) + '\n',
                  '首选命中率： ' + str((self.mFirstHitCount * 1.000) / self.mTotalCount) + '\n',
                  '首屏命中数： ' + str(self.mTotalCount - self.mMissCount) + '\n',
                  '首屏命中率(带权重): ' + str(((self.mHitNotFirstWeight + self.mFirstHitWeight) * 1.000) / self.mTotalWeight) + '\n',
                  '首屏命中率： ' + str(((self.mTotalCount - self.mMissCount) * 1.000) / self.mTotalCount) + '\n',
                  '输入法名称: ' + self.imeInfo.PackageName + '\n',
                  '输入法Version Name： ' + self.imeInfo.VersionName + '\n',
                  '输入法Version Code： ' + self.imeInfo.VersionCode + '\n',
                  'Log文件校验结果: ' + ('正确' if self.mIsCorrect else '错误')]
        #target = target.encode("UTF-8")
        analyseFile.writelines(target)
        return


    def main(self):
        if self.downloadFile():
            self.mRawConfig = open(LOCAL_CONFIG_FILE, 'r')
            self.getImeInfo()
            self.analyse()

        self.mIsCorrect = self.checkLog()

        self.writeAnalyseResult()


if __name__ == '__main__':
    reporter = report()
    reporter.main()