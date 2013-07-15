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
LOCAL_RESULT_FILE = './result.txt'
#下载到本地进行分析的raw.config文件
LOCAL_CONFIG_FILE = './raw.config'
#FTP文件路径
REMOTE_FILE_PATH = '/WordCrawler'
#raw.config文件路径
REMOTE_CONFIG_PATH = '/WordCrawler/raw.config'
#分析结果文件
ANALYSE_FILE_PATH = 'analyse_result.txt'


class ImeInfo:
    VersionName = ""
    VersionCode = ""
    PackageName = ""


class report:
    imeInfo = ImeInfo()
    #总输入Case个数
    mTotalInputCount = 0
    #总运行Case个数
    mTotalRanCount = 0
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
    #raw.config文件全部内容
    mRawConfigLines = ['']
    #没有运行的Case记录
    mMissedRunCase = ''
    #没有在首位的case
    mNotFirstCase = ''

    def downloadFile(self):
        if os.path.isfile(LOCAL_RESULT_FILE) and os.path.exists(LOCAL_RESULT_FILE):
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
        self.mTotalRanCount += 1
        lines = oneResult.split('\n')
        weightStr = "error"
        try:
            weightStr = self.getCaseWeight(self.mTotalRanCount, lines[0][7:])
            weight = int(weightStr)
        except ValueError:
            print weightStr + ", error in convert weight!"
            print lines[0]
            weight = 0

        self.mTotalWeight += weight

        for line in lines:
            if line.__contains__('target:'):
                if line.__contains__('target:1'):
                    self.mFirstHitCount += 1
                    self.mFirstHitWeight += weight
                elif line.__contains__('target:-1'):
                    self.mMissCount += 1
                    self.mMissWeight += weight
                    self.mNotFirstCase += "第" + str(self.mTotalRanCount) + "个运行的Case:\n" +\
                                         "===wordstart===\n" + oneResult + "===wordend===\n"
                else:
                    self.mHitNotFirstCount += 1
                    self.mHitNotFirstWeight += weight
                    self.mNotFirstCase += "第" + str(self.mTotalRanCount) + "个运行的Case:\n" +\
                                         "===wordstart===\n" + oneResult + "===wordend===\n"

        return

    def analyse(self):
        oneResult = ''
        resultFile = open(LOCAL_RESULT_FILE, 'r')
        self.mNotFirstCase = "==============\n"
        for line in resultFile:
            line.decode('UTF-8')
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

    def getCaseWeight(self, curCount, inputStr):
        #下标和个数不一样，换算一下
        index = curCount - 1
        line = ""
        pinyin = inputStr[:inputStr.index('\t')]
        hanzi = inputStr[inputStr.index('\t') + 1:]
        #找到指定Case的权重值
        for i in range(index, self.mRawConfigLines.__len__()):
            oneInputCase = self.mRawConfigLines[i]
            if oneInputCase.__contains__(hanzi + ',' + pinyin):
                index  = i
                break
        try:
            line = self.mRawConfigLines[index]
        except IndexError:
            print 'index: ' + str(index) + ', curCount: ' + str(curCount)
            raise
        if line.__contains__(hanzi + ',' + pinyin):
            lines = line.split(',')
            weights = lines[lines.__len__() - 1].split("\"")
            return weights[weights.__len__() - 2]
        else:
            print inputStr + ', 没有读取到正确的权重值！'
            return "0"

    def checkLog(self):
        if self.mTotalRanCount == self.mFirstHitCount + self.mHitNotFirstCount + self.mMissCount:
            print '个数校验成功！'
            if self.mTotalWeight == self.mFirstHitWeight + self.mHitNotFirstWeight + self.mMissWeight:
                print '权重校验成功！'
                return True
        else:
            return False

    def writeAnalyseResult(self):
        for i in range(0, self.mRawConfigLines.__len__()):
            if not self.mRawConfigLines[i].__contains__(',#'):
                self.mTotalInputCount += 1
        analyseFile = open(ANALYSE_FILE_PATH, 'w')
        target = ['1. 输入case总数:  ' + str(self.mTotalInputCount) + '\n',
                  '2. 运行case总数:  ' + str(self.mTotalRanCount) + '\n',
                  '3. 首选:  ' + '\n',
                  '\t3.1 首选命中总权重:  ' + str(self.mFirstHitWeight) + '\n' ,
                  '\t3.2 首选命中数:  ' + str(self.mFirstHitCount) + '\n',
                  '\t3.3 首选命中率(带权重):  ' + str((self.mFirstHitWeight * 1.000) / self.mTotalWeight) + '\n',
                  '\t3.4 首选命中率:  ' + str((self.mFirstHitCount * 1.000) / self.mTotalRanCount) + '\n',
                  '4. 首屏:  ' + '\n',
                  '\t4.1 首屏命中总权重:  ' + str((self.mHitNotFirstWeight + self.mFirstHitWeight)) + '\n',
                  '\t4.2 首屏命中数:  ' + str(self.mTotalRanCount - self.mMissCount) + '\n',
                  '\t4.3 首屏命中率(带权重):  ' + str(((self.mHitNotFirstWeight + self.mFirstHitWeight) * 1.000) / self.mTotalWeight) + '\n',
                  '\t4.4 首屏命中率:  ' + str(((self.mTotalRanCount - self.mMissCount) * 1.000) / self.mTotalRanCount) + '\n',
                  '5. 输入法信息:  ' + '\n',
                  '\t5.1 输入法名称:  ' + self.imeInfo.PackageName + '\n',
                  '\t5.2 输入法Version Name:  ' + self.imeInfo.VersionName + '\n',
                  '\t5.3 输入法Version Code:  ' + self.imeInfo.VersionCode + '\n',
                  '6. 结果校验:  ' + '\n',
                  '\t6.1 Log文件校验结果:  ' + ('权重值校验正确, case个数校验正确！' if self.mIsCorrect else '错误') + '\n',
                  '\t6.2 没有运行的Case:  ' + '\n\n' + self.mMissedRunCase + '\n',
                  '\t6.3 没有在首位的case:  ' + '\n\n' + self.mNotFirstCase + '\n']
        analyseFile.writelines(target)
        return

    def checkMissedRunCase(self):
        checkResult = ''
        missedRunCount = 0
        resultFile = open(LOCAL_RESULT_FILE, 'r')
        ranCaseList = []
        for line in resultFile:
            #line.decode('UTF-8')
            if line.__contains__('pinyin:'):
                ranCaseList.append(line.split(':')[1])
        for case in self.mRawConfigLines:
            oneInputCase = case.split('\"')[1].split(',')
            targetInputCase = oneInputCase[1] + '\t' + oneInputCase[0] + '\n'
            if not targetInputCase in ranCaseList:
                missedRunCount += 1
                checkResult += '没有运行：' + case
        if missedRunCount != 0:
            checkResult += '有' + str(missedRunCount) + '个case没有运行！'
        return checkResult

    def main(self):
        if os.path.isfile(LOCAL_CONFIG_FILE) and os.path.isfile(LOCAL_RESULT_FILE):
            self.mRawConfigLines = open(LOCAL_CONFIG_FILE, 'r').readlines()
            self.getImeInfo()
            self.analyse()
            self.mMissedRunCase = self.checkMissedRunCase()
            self.mIsCorrect = self.checkLog()
            self.writeAnalyseResult()
        else:
            print  LOCAL_CONFIG_FILE + ' 或者 ' + LOCAL_RESULT_FILE +  '文件不存在！'


if __name__ == '__main__':
    reporter = report()
    reporter.main()