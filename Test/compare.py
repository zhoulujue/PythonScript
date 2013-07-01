# coding=utf-8
__author__ = 'Michael'

import os

class comparer:
    mLinesOfErrorLog = []
    mLinesOfResultLog = []
    mSplitResults = []

    def readErrorLog(self):
        lines = []
        ErrorLogFile = open("../Result/ErrLog.txt")
        rawLines = ErrorLogFile.readlines()
        for line in rawLines:
            if line.__contains__("  >>  "):
                pinyin = line.split("  >>  ")[1]
                hanzi = line[line.index("Expect:") + "Expect:".__len__(): line.index(", Real:")]
                lines.append(pinyin + '\t' + hanzi)
        return lines

    def readResultLog(self):
        lines = []
        oneResult = ''
        resultFile = open("../Result/analyse_result.txt", 'r')
        for line in resultFile:
            line.decode('UTF-8')
            if line.__contains__('pinyin:'):
                case = line.split("pinyin:")[1]
                case = case[:case.index('\n')]
                lines.append(case)
        return lines

    def readSplitResults(self):

        oneResult = ''
        splitResults = []
        resultFile = open("../Result/analyse_result.txt", 'r')
        for line in resultFile:
            if line.__contains__("===wordstart==="):
                oneResult = ''
            elif line.__contains__("===wordend==="):
                splitResults.append(oneResult)
            else:
                oneResult += line
        return splitResults

    def writeDiff(self):
        diffCount = 0
        compareResult = open("../Result/compare_result.txt", 'w')
        differences = []

        largerCount = self.mLinesOfErrorLog.__len__()
        smallerCount = self.mLinesOfResultLog.__len__()

        differences.append("ErrorLog个数：" + str(largerCount) + '\n')
        differences.append("analyse_result个数：" + str(smallerCount) + '\n\n')

        if largerCount == smallerCount:
            differences.append("一模一样，没啥不一样的！")

        if largerCount < smallerCount:
            temp = largerCount
            largerCount = smallerCount
            smallerCount = temp
            print '\n两个文件的case个数不一样！\n'

        index = 0
        count = 0
        foundInOld = False
        differences.append("#######新工具不在首位，老工具在首位#######\n")
        for case in self.mLinesOfResultLog:
            if not case in self.mLinesOfErrorLog:
                differences.append("==="+ str(index) +"===\n" + case + "\n\n")
                differences.append(self.mSplitResults[index] + '\n')
            index += 1

        differences.append("#######老工具不在首位，新工具在首位#######\n")
        index = 0

        foundInNew = False
        for error in self.mLinesOfErrorLog:
            if not error in self.mLinesOfResultLog:
                index += 1
                differences.append("===" + str(index) +"===\n" + error + "\n\n")


        compareResult.writelines(differences)

    def main(self):
        self.mLinesOfErrorLog = self.readErrorLog()
        self.mLinesOfResultLog = self.readResultLog()
        self.mSplitResults = self.readSplitResults()
        self.writeDiff()

if __name__ == '__main__':
    test = comparer()
    test.main()

