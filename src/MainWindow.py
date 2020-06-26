# -*- coding: utf-8 -*-

import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem


class State:
    def __init__(self, root, content, isroot, parent, idx):
        self.root = root  # 基本推导式集
        self.content = content  # 此状态内的推导式集
        self.isroot = isroot  # 是否为IO
        self.parent = parent  # 父节点
        self.next = {}  # 子节点
        self.idx = idx  # 状态集编号
        self.VN = []  # 非终结符集
        self.Symbol = []  # 符号集
        self.EndNum = {}  # 文法中已推导至结束的式子数和式子总数

        if root:
            self.GetSymbol()
            self.Generate()
            self.FindNext()

    # 自己是否为终结态
    def End(self):
        cnt = 0
        for c in self.content:
            if c[-1] == '·':
                cnt += 1
        self.EndNum = {'end': cnt, 'all': len(self.content)}

    # 得到符号集
    def GetSymbol(self):
        # 非终结符
        for c in self.root:
            self.VN.append(c[0])
        self.VN = list(set(self.VN))
        # 所有符号
        for c in self.root:
            for r in c:
                if r not in self.Symbol and r not in ['·', '-', '>']:
                    self.Symbol.append(r)

    # 生成此状态集中的推导式
    def Generate(self):
        # 根节点内的推导式集就是基本推导式集
        if self.isroot:
            self.content = self.root
        # 非根节点的推导式集
        else:
            new_content = []

            # 将父节点传来的推导式中·后移一位
            for c in self.content:
                c = c.split('·')
                c = c[0] + c[1][0] + '·' + c[1][1:]
                new_content.append(c)

            # 若存在·VN的形式，则将所有VN->*的推导式加入
            for c in new_content:
                if c.index('·') == len(c) - 2 and c[-1] in self.VN:
                    for r in self.root:
                        if r[0] == c[-1]:
                            new_content.append(r)

            new_content = list(set(new_content))
            self.content = new_content

    # 得到每个符号对应的下一个状态中的推导式
    def FindNext(self):
        for s in self.Symbol:
            self.next[s] = []
        for c in self.content:
            pos = c.index('·')
            if pos != len(c) - 1:
                # ·之后符号对应的next里加入这个式子
                self.next[c[pos + 1]].append(c)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("Analyzer")
        MainWindow.resize(1200, 750)
        MainWindow.setFixedSize(1200, 750)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        MainWindow.setFont(font)
        self.Base = QtWidgets.QWidget(MainWindow)
        self.Base.setObjectName("Base")
        self.InputArea = QtWidgets.QTextEdit(self.Base)
        self.InputArea.setGeometry(QtCore.QRect(50, 40, 520, 300))
        self.InputArea.setObjectName("InputArea")
        self.FirstSet = QtWidgets.QTextEdit(self.Base)
        self.FirstSet.setGeometry(QtCore.QRect(50, 375, 520, 150))
        self.FirstSet.setObjectName("FirstSet")
        self.FollowSet = QtWidgets.QTextEdit(self.Base)
        self.FollowSet.setGeometry(QtCore.QRect(50, 560, 520, 150))
        self.FollowSet.setObjectName("FollowSet")
        self.AnalyticalTable = QtWidgets.QTableWidget(self.Base)
        self.AnalyticalTable.setGeometry(QtCore.QRect(630, 40, 520, 485))
        self.AnalyticalTable.setObjectName("AnalyticalTable")
        self.AnalyticalTable.setColumnCount(50)
        self.AnalyticalTable.setRowCount(50)
        self.RunButton = QtWidgets.QPushButton(self.Base)
        self.RunButton.setGeometry(QtCore.QRect(670, 570, 170, 45))
        self.RunButton.setObjectName("RunButton")
        self.ClearButton = QtWidgets.QPushButton(self.Base)
        self.ClearButton.setGeometry(QtCore.QRect(940, 570, 170, 45))
        self.ClearButton.setObjectName("ClearButton")
        self.HelpButton = QtWidgets.QPushButton(self.Base)
        self.HelpButton.setGeometry(QtCore.QRect(940, 655, 170, 45))
        self.HelpButton.setObjectName("HelpButton")
        self.OpenButton = QtWidgets.QPushButton(self.Base)
        self.OpenButton.setGeometry(QtCore.QRect(670, 655, 170, 45))
        self.OpenButton.setObjectName("OpenButton")
        self.label_1 = QtWidgets.QLabel(self.Base)
        self.label_1.setGeometry(QtCore.QRect(50, 15, 121, 21))
        self.label_1.setObjectName("label_1")
        self.label_2 = QtWidgets.QLabel(self.Base)
        self.label_2.setGeometry(QtCore.QRect(50, 350, 121, 21))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.Base)
        self.label_3.setGeometry(QtCore.QRect(50, 535, 121, 21))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.Base)
        self.label_4.setGeometry(QtCore.QRect(630, 15, 121, 21))
        self.label_4.setObjectName("label_4")
        MainWindow.setCentralWidget(self.Base)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # 自定义变量
        self.SymbolSet = []  # 符号集，保存每一个符号
        self.Derivation = {}  # 推导式集，以字典形式保存，key为str型左侧非终结符，value为list型右侧候选式
        self.First = {}  # First集，
        self.Follow = {}  # Follow集
        self.VT = []  # 终结符集
        self.VN = []  # 非终结符集
        self.e_list = ['ε']  # 可推导出ε的符号集
        self.I = []  # 状态集

        # 自定义槽函数
        self.OpenButton.clicked.connect(self.OpenFile)
        self.RunButton.clicked.connect(self.Analyze)
        self.ClearButton.clicked.connect(self.Clear)
        self.HelpButton.clicked.connect(self.Help)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Analyzer"))
        self.InputArea.setPlaceholderText(_translate("MainWindow", "输入文法前请先确认符合同目录下操作手册.docx中的规范！"))
        self.RunButton.setText(_translate("MainWindow", "分析"))
        self.ClearButton.setText(_translate("MainWindow", "清空"))
        self.HelpButton.setText(_translate("MainWindow", "帮助"))
        self.OpenButton.setText(_translate("MainWindow", "从文件打开.."))
        self.label_1.setText(_translate("MainWindow", "输入区"))
        self.label_2.setText(_translate("MainWindow", "First集"))
        self.label_3.setText(_translate("MainWindow", "Follow集"))
        self.label_4.setText(_translate("MainWindow", "分析表"))

    # 从文件读入文法
    def OpenFile(self):
        self.Clear()
        fname = QFileDialog.getOpenFileName(self.OpenButton, '打开文件', '.')
        if fname[0]:
            f = open(fname[0], 'r', encoding='utf-8')
            with f:
                data = f.read()
                self.InputArea.setText(data)

    # 分析文法
    def Analyze(self):
        if self.SymbolSet:
            return
        content = self.InputArea.toPlainText()
        if content == '':
            self.FirstSet.setText('没有输入！')
            self.FollowSet.setText('没有输入！')
        else:
            data = self.InputArea.toPlainText()
            # 获取符号集
            for c in data:
                if c != '|' and c != '-' and c != '>' and c != '\n' and c != ' ' and c not in self.SymbolSet:
                    self.SymbolSet.append(c)
            # 按行拆分，读取推导规则，保存为字典格式
            data = data.split('\n')
            for line in data:
                if line == '':
                    continue
                line = line.split('->')
                self.Derivation[line[0]] = line[1].split('|')  # 左侧为key，右侧为value（list格式）

            # 建立终结符集和非终结符集
            for s in self.SymbolSet:
                if s in self.Derivation.keys():
                    self.VN.append(s)
                else:
                    self.VT.append(s)

            # 建立First集
            for c in self.SymbolSet:  # 初始化
                self.First[c] = []
            for c in self.SymbolSet:  # 建立First集
                self.FindFirst(c)

            for key in self.First.keys():  # 去重
                self.First[key] = list(set(self.First[key]))
            # 设置文本显示，将self.First（字典）转换为字符串，添加换行，去掉空格和单引号
            text = '符号的First集：\n'
            for item in self.First.items():
                # 去掉引号，将list的[]换成集合的{}
                text += 'First(' + str(item[0]).replace('\'', '') + '): ' \
                        + str(item[1]).replace('\'', '').replace('[', '{').replace(']', '}') \
                        + '\n'
            text += '\n候选式的First集：\n'
            c_list = []
            for value in self.Derivation.values():
                for c in value:
                    if c not in c_list and c != 'ε':
                        c_list.append(c)
            for c in c_list:
                f = self.cFirst(c)
                f = str(f).replace('\'', '').replace('[', '{').replace(']', '}') + '\n'
                text += 'First(' + str(c).replace('\'', '') + '): ' + f
            self.FirstSet.setText(text)

            # 统计能推出ε的符号
            self.FindE()

            # 建立Follow集
            for c in self.VN:  # Follow集只考虑非终结符
                self.Follow[c] = []
            self.FindFollow()

            for key in self.Follow.keys():  # 去重
                self.Follow[key] = list(set(self.Follow[key]))
            # 设置文本显示，将self.Follow（字典）转换为字符串，添加换行，去掉空格和单引号
            text = ''
            for item in self.Follow.items():
                # 去掉引号，将list的[]换成集合的{}
                text += 'Follow(' + str(item[0]).replace('\'', '') + '): ' \
                        + str(item[1]).replace('\'', '').replace('[', '{').replace(']', '}') \
                        + '\n'
            self.FollowSet.setText(text)

            # 构建分析表
            self.VT.append('#')
            self.LL1()
            self.LR0()

    # 寻找非终结符c的First集
    def FindFirst(self, c):
        # 终结符的First集为自己
        if c not in self.VN:
            self.First[c] = [c]
            return self.First[c]

        # 非终结符遍历其候选式的首字母：
        else:
            for s in self.Derivation[c]:
                # 终结符或ε直接加入左侧符号的First集中
                if s[0] not in self.VN:
                    self.First[c].append(s[0])
                # 非终结符
                else:
                    # 将其First集加入左侧符号的First集中
                    if c != s[0]:
                        extend = self.FindFirst(s[0])
                        # 若开头的非终结符能推出ε但此候选式长度不为1，其First集中ε不会加入左侧符号的First集中
                        if len(s) != 1 and 'ε' in extend:
                            extend.remove('ε')
                        self.First[c].extend(extend)
                        # 若开头的非终结符能推出ε，则将其下一个符号的First集加入左侧符号的First集中
                        if 'ε' in self.Derivation[s[0]] and len(s) != 1:
                            extend = self.FindFirst(s[1])
                            self.First[c].extend(extend)
            return self.First[c]

    # 建立文法的Follow集
    def FindFollow(self):
        self.Follow[self.SymbolSet[0]].append('#')
        # while中的过程直至所有的Follow集不再增大
        isChange = True
        while isChange:
            isChange = False
            # 遍历每一条推导式
            for key, value in self.Derivation.items():  # 每条推导式
                for i in range(len(value)):  # 每条候选式value[i]
                    for j in range(len(value[i])):  # 候选式中的每个符号value[i][j]
                        if value[i][j] in self.VN:  # 只考虑非终结符
                            l = len(value[i])
                            # a->*b或a->*bc且c->ε，将Follow(a)加入Follow(b)
                            # value[i][j]是结尾字符
                            if j == l - 1:
                                l_o = len(self.Follow[value[i][j]])  # 原本的长度
                                self.Follow[value[i][j]].extend(self.Follow[key])  # 将Follow(key)加入Follow(value[i][j])
                                self.Follow[value[i][j]] = list(set(self.Follow[value[i][j]]))  # 去重
                                if len(self.Follow[value[i][j]]) != l_o:  # 检查是否发生变化
                                    isChange = True
                            # a->*bc且c->ε，将Follow(a)加入Follow(b)
                            # value[i][j]是倒数第二个字符，且value[i][j+1]是非终结符
                            elif (j == l - 2) and (value[i][j + 1] in self.VN):
                                l_o = len(self.Follow[value[i][j]])  # 原本的长度
                                extend = self.First[value[i][j + 1]]
                                if 'ε' in extend:
                                    extend.remove('ε')
                                self.Follow[value[i][j]].extend(extend)  # 将First(value[i][j+1])加入Follow(value[i][j])
                                self.Follow[value[i][j]] = list(set(self.Follow[value[i][j]]))  # 去重
                                if len(self.Follow[value[i][j]]) != l_o:  # 检查是否发生变化
                                    isChange = True
                                # value[i][j+1]能推出ε
                                if 'ε' in self.Derivation[value[i][j + 1]]:
                                    l_o = len(self.Follow[value[i][j]])  # 原本的长度
                                    self.Follow[value[i][j]].extend(
                                        self.Follow[key])  # 将Follow(key)加入Follow(value[i][j])
                                    self.Follow[value[i][j]] = list(set(self.Follow[value[i][j]]))  # 去重
                                    if len(self.Follow[value[i][j]]) != l_o:  # 检查是否发生变化
                                        isChange = True
                            # a->*bc*，将First(c)-{ε}加入Follow(b)
                            else:
                                l_o = len(self.Follow[value[i][j]])  # 原本的长度
                                extend = self.First[value[i][j + 1]]
                                if 'ε' in extend:
                                    extend.remove('ε')
                                self.Follow[value[i][j]].extend(extend)  # 将First(value[i][j+1])加入Follow(value[i][j])
                                self.Follow[value[i][j]] = list(set(self.Follow[value[i][j]]))  # 去重
                                if len(self.Follow[value[i][j]]) != l_o:  # 检查是否发生变化
                                    isChange = True

    # 判断是否为LL(1)文法
    def isLL1(self):
        # 遍历每个推导式
        for key, value in self.Derivation.items():

            # 同一个符号的候选式至多只能有一个能推出ε
            cnt = 0
            for c in value:
                if self.isE(c):
                    cnt += 1
                if cnt > 1:
                    return False

            c_e = []  # 能推出ε的候选式
            c_none = []  # 不能推出ε的候选式

            for c in value:
                # 存在左递归则不是LL(1)文法
                if key == c[0]:
                    return False

                # 候选式按能否推出ε分类
                if self.isE(c):
                    c_e.append(c)
                else:
                    c_none.append(c)

            # 对不能推出ε的候选式，两两First交集为空
            if len(c_none) > 1:  # 至少得有两个候选式
                for i in c_none:  # 两两比较
                    for j in c_none:
                        if i == j:  # 不能自己跟自己比
                            continue
                        for v in self.Derivation.values():  # 要是同一个符号的候选式
                            if i in v and j in v:
                                i_first = set(self.cFirst(i))
                                j_first = set(self.cFirst(j))
                                if i_first & j_first == set():  # 交集为空集
                                    continue
                                else:
                                    return False

            # 对能推出ε的候选式，First(候选式)与Follow(key)交集为空
            for i in c_e:
                i_first = set(self.cFirst(i))
                key_first = set(self.Follow[key])
                if i_first & key_first == set():  # 交集为空集
                    continue
                else:
                    return False

        return True

    # 建立LL分析表
    def LL1(self):
        if self.isLL1():

            # 表头部分
            self.AnalyticalTable.setItem(0, 0, QTableWidgetItem('LL Parser'))
            self.AnalyticalTable.setSpan(0, 0, 1, len(self.VT) + 1)

            column = 1
            for i in self.VT:
                if i != 'ε':
                    self.AnalyticalTable.setItem(1, column, QTableWidgetItem(i))
                    column += 1
            row = 2
            for i in self.VN:
                self.AnalyticalTable.setItem(row, 0, QTableWidgetItem(i))
                row += 1
            # 坐标：
            # 行：在self.VN中的坐标+2
            # 列：在self.VT中的坐标+1
            for key, value in self.Derivation.items():
                for c in value:
                    c_first = self.cFirst(c)
                    for a in c_first:
                        if a != 'ε':
                            x = self.VN.index(key) + 2
                            y = self.VT.index(a)
                            if 'ε' in self.VT:
                                if y < self.VT.index('ε'):
                                    y += 1
                            else:
                                y += 1
                            content = QTableWidgetItem(key + '->' + c)
                            self.AnalyticalTable.setItem(x, y, content)
                            if 'ε' in self.First[a]:
                                for b in self.Follow[key]:
                                    x = self.VN.index(key) + 2
                                    y = self.VT.index(b) + 1
                                    content = QTableWidgetItem(key + '->' + c)
                                    self.AnalyticalTable.setItem(x, y, content)

        # 不是LL(1)文法
        else:
            self.AnalyticalTable.setItem(0, 0, QTableWidgetItem('This is not a LL grammer.'))
            self.AnalyticalTable.setColumnWidth(0, 200)

    # 建立LR分析表
    def LR0(self):

        # 建立状态集
        root = []
        # 每个结果不是ε的推导式，在候选式前加·，放进root
        for key, value in self.Derivation.items():
            for c in value:
                root.append(key + '->·' + c)
        idx = 0
        I0 = State(root, [], True, None, idx)
        idx += 1
        I = [I0]  # 状态集
        isChange = True
        while isChange:
            isChange = False
            # 查看每个状态集是否还能推导
            for i in I:
                # 检查next中的每个对象
                for key, value in i.next.items():
                    # 若value为列表，则要将其转换为State
                    if type(value) == list and value != []:
                        isExist = False
                        # 若value对应的State已经存在于I中，则直接建立引用
                        for j in I:
                            value_new = []
                            for c in value:
                                c = c.split('·')
                                c = c[0] + c[1][0] + '·' + c[1][1:]
                                value_new.append(c)
                            if j.content == value_new:
                                i.next[key] = j
                                isExist = True
                                isChange = True
                                break
                        # 若不存在，则建立新的State
                        if not isExist:
                            i.next[key] = State(root, value, False, i, idx)
                            I.append(i.next[key])
                            idx += 1
                            isChange = True

        I.insert(1, State([], [], None, None, None))  # 增广
        for i in I:
            i.End()  # 得到其中·在最后的式子的数量

        # 表头部分
        row = len(self.VN) + 6
        column = 1
        self.AnalyticalTable.setItem(row - 3, 0, QTableWidgetItem('LR Parser'))
        self.AnalyticalTable.setSpan(row - 3, 0, 1, len(self.VT) + len(self.VN) + 1)
        self.AnalyticalTable.setItem(row - 2, 1, QTableWidgetItem('Action'))
        self.AnalyticalTable.setSpan(row - 2, 1, 1, len(self.VT))
        self.AnalyticalTable.setItem(row - 2, len(self.VT) + 1, QTableWidgetItem('Goto'))
        self.AnalyticalTable.setSpan(row - 2, len(self.VT) + 1, 1, len(self.VN))
        for i in self.VT:
            if i != 'ε':
                self.AnalyticalTable.setItem(row - 1, column, QTableWidgetItem(i))
                column += 1
        for i in self.VN:
            self.AnalyticalTable.setItem(row - 1, column+1, QTableWidgetItem(i))
            column += 1
        for i in range(len(I)):
            self.AnalyticalTable.setItem(row, 0, QTableWidgetItem(str(i)))
            row += 1

        # 填表

        # Ia通过key到Ib，则(a, key) = sb/b，取决于key是终结符还是非终结符
        # key∈VT, key = self.VT.index(key)+1
        # key∈VN, key = self.VN.index(key)+1+len(self.VT)
        # 遍历I：
        # 若其中只有一个推导式且·在末尾，则全填rx
        # 若有多个推导式，一部位·在末尾，则这几个式子对应的格子填rx，key为从这个式子到终结态的key

        isLR = True
        # sb/b
        for i in range(len(I)):
            for key, value in I[i].next.items():
                if value:  # 每一对Ia->Ib
                    x = len(self.VN) + 6 + i
                    # key为终结符，填sb
                    if key in self.VT:
                        y = self.VT.index(key) + 1
                        source = 's' + str(I.index(value))
                        if self.AnalyticalTable.item(x, y):
                            isLR = False
                        else:
                            self.AnalyticalTable.setItem(x, y, QTableWidgetItem(source))

                    # key为非终结符，填b
                    else:
                        y = self.VN.index(key) + 1 + len(self.VT)
                        source = str(I.index(value))
                        if self.AnalyticalTable.item(x, y):
                            isLR = False
                        else:
                            self.AnalyticalTable.setItem(x, y, QTableWidgetItem(source))
        # rb
        for i in range(len(I)):
            x = len(self.VN) + 6 + i
            # I[i]中只有一个式子且·在末尾，则在这一行的Action下全填rx，x为该式子在root对应式子的编号
            if I[i].EndNum['end'] == 1 and I[i].EndNum['all'] == 1:
                c = I[i].content[0][:-1].split('->')
                c = c[0] + '->·' + c[1]
                source = root.index(c) + 1
                source = 'r' + str(source)
                for y in range(1, len(self.VT)):
                    if self.AnalyticalTable.item(x, y):
                        isLR = False
                    else:
                        self.AnalyticalTable.setItem(x, y, QTableWidgetItem(source))
            # I[i]中一部分式子·在末尾，则在#列下填rx
            else:
                for c in I[i].content:
                    if c[-1] == '·':
                        c = c[:-1].split('->')
                        c = c[0] + '->·' + c[1]
                        source = root.index(c) + 1
                        source = 'r' + str(source)
                        y = len(self.VT)
                        if self.AnalyticalTable.item(x, y):
                            isLR = False
                        else:
                            self.AnalyticalTable.setItem(x, y, QTableWidgetItem(source))
        self.AnalyticalTable.setItem(len(self.VN) + 6 + 1, self.VT.index('#') + 1, QTableWidgetItem('acc'))

        for key, value in self.Derivation.items():
            for c in value:
                # 存在左递归则不是LR文法
                if key == c[0]:
                    isLR = False
        if not isLR:
            for x in range(len(self.VN) + 6, len(self.VN) + 7 + len(I)):
                for y in range(1, len(self.VT) + len(self.VN) + 1):
                    self.AnalyticalTable.setItem(x, y, QTableWidgetItem(''))
            self.AnalyticalTable.setItem(len(self.VN) + 3, 0, QTableWidgetItem('This is not a LR grammer.'))

    # 判断候选式是否能推导出ε
    def isE(self, c):
        if c == 'ε':
            return True
        # 有终结符存在必不可能推导出ε
        for i in c:
            if i in self.VT:
                return False
        # 无终结符，则遍历每个符号，若全都能推出ε，则此候选式能推出ε
        for i in c:
            if i in self.e_list:
                continue
            else:
                return False

        return True

    # 建立ε集
    def FindE(self):
        isChange = True
        while isChange:
            isChange = False
            for key, value in self.Derivation.items():
                for c in value:
                    if c in self.e_list and key not in self.e_list:  # 如果c可以推出ε，那key也可以
                        self.e_list.append(key)
                        isChange = True

    # 求候选式的First集
    def cFirst(self, c):
        # 终结符开头，则其First集为这个终结符
        if c[0] in self.VT:
            return [c[0]]
        # 非终结符，则返回其First集
        else:
            result = self.First[c[0]]
            # 若c[0]能推出ε，则还要加上其后符号的First集
            if 'ε' in self.Derivation[c[0]] and len(c) != 1:
                result.extend(self.First[c[1]])
            return list(set(result))

    # 重置为初始状态
    def Clear(self):
        self.InputArea.clear()
        self.FirstSet.clear()
        self.FollowSet.clear()
        self.AnalyticalTable.clear()
        self.AnalyticalTable.setColumnCount(0)
        self.AnalyticalTable.setRowCount(0)
        self.AnalyticalTable.setColumnCount(50)
        self.AnalyticalTable.setRowCount(50)
        self.SymbolSet = []  # 符号集，保存每一个符号
        self.Derivation = {}  # 推导式集，以字典形式保存，key为str型左侧非终结符，value为list型右侧候选式
        self.First = {}  # First集
        self.Follow = {}  # Follow集
        self.VT = []  # 终结符集
        self.VN = []  # 非终结符集
        self.e_list = ['ε']  # 可推导出ε的符号集
        self.I = []  # 状态集

    # 帮助
    def Help(self):
        os.startfile('操作手册.docx')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(gui)
    gui.show()
    sys.exit(app.exec_())
