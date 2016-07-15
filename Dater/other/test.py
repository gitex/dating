#!/usr/bin/env python
# -*- coding: utf-8 -*-

def sumLists(aList):
    half = len(aList)//2
    leftHalf = aList[half:]
    rightHalf = aList[:half]
    if len(aList) == 1:
        return aList[0]
    else:
        sumOfLeft = sumLists(leftHalf[1:])
        resultLeft = leftHalf[0] + sumOfLeft
        sumOfRight = sumLists(rightHalf[1:])
        resultRight = rightHalf[0] + sumOfRight
        return resultLeft + resultRight

def sum_list(l):
    if len(list) == 1:
        return