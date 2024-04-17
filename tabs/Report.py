import numpy as np
import pandas as pd

import streamlit as st


def showReport(metaData):
    problemDataToDataFrame(metaData)
    unbalancedDataToDataFrame(metaData)
    balancedDataToDataFrame(metaData)
        
        
def saveReport(metaData):
    reportStr = []
    
    addProblemData(metaData, reportStr)
    addSeparator(reportStr, amount=2)
    appendUnbalancedLineData(metaData, reportStr)
    addSeparator(reportStr, amount=2)
    appendBalancedLineData(metaData, reportStr)
    
    return reportStr


def addProblemData(metaData, reportStr):
    unbalancedGraph = metaData['unBalancedGraph']
    totalProcessingTime = sum(
        unbalancedGraph.nodes[k].get('weight') for k in unbalancedGraph.nodes
    )

    reportStr.append("The demand                                    : "+"{:12.2f} ".format(metaData['demand']) + "units")
    reportStr.append("Total available time for processing           : "+"{:12.2f} ".format(metaData['totalWorkTime']) + metaData['timeUnit'])
    reportStr.append("The takt time for this process                : "+"{:12.2f} ".format(metaData['taktTime']) + metaData['timeUnit'])
    reportStr.append("The total task time for this line             : "+"{:12.2f} ".format(totalProcessingTime) + metaData['timeUnit'])
    reportStr.append("Number of nodes                               : "+"{:12.0f} ".format(len(unbalancedGraph.nodes.keys())))
    reportStr.append("Number of edges                               : "+"{:12.0f} ".format(len(unbalancedGraph.edges)))
    
    
def addSeparator(reportStr, amount):
    for _ in range(amount):
        reportStr.append("")
   
    
def appendUnbalancedLineData(metaData, reportStr):
    unbalancedGraph = metaData['unBalancedGraph']
    idleTime = sum(
        metaData['taktTime'] - unbalancedGraph.nodes[k].get('weight')
        for k in unbalancedGraph.nodes
    )
    smoothnessIndex = np.sqrt(
        sum(np.power((metaData['taktTime'] - unbalancedGraph.nodes[k].get('weight')), 2,)
            for k in unbalancedGraph.nodes
        )
    )

    totalProcessingTime = sum(
        unbalancedGraph.nodes[k].get('weight') for k in unbalancedGraph.nodes
    )

    reportStr.append(" ----------------------------------------- Unbalanced Line --------------------------------------")
    reportStr.append("       task name                                                          task time   idle time ")
    reportStr.append(" ------------------------------------------------------------------------------------------------")

    res = ["["+"{0:>3}".format(k)+"] "+"{0:<64}"
           .format(unbalancedGraph.nodes[k].get('name'))+"{:12.2f}"
           .format(unbalancedGraph.nodes[k].get('weight'))+"{:12.2f}"
           .format(metaData['taktTime'] - unbalancedGraph.nodes[k].get('weight')) for k in unbalancedGraph.nodes]

    [reportStr.append(f"{res[k]}") for k in range(len(res))]
    addSeparator(reportStr, amount=1)
    reportStr.append("Total idle time                                 : "+"{:12.2f} ".format(float(idleTime)) + metaData['timeUnit'])
    reportStr.append("Smoothness index                                : "+"{:12.2f} ".format(smoothnessIndex))
    reportStr.append("Line efficiency                                 : "+"{:12.2f} %".format((totalProcessingTime /(totalProcessingTime+idleTime)) * 100))

    
def appendBalancedLineData(metaData, reportStr):
    balancedGraph = metaData['balancedGraph']
    unbalancedGraph = metaData['unBalancedGraph']

    idleTime = sum(
        metaData['taktTime'] - balancedGraph.nodes[k].get('weight')
        for k in balancedGraph.nodes
    )

    smoothnessIndex = np.sqrt(
        sum(
            np.power((metaData['taktTime'] - balancedGraph.nodes[k].get('weight')), 2)
            for k in balancedGraph.nodes
        )
    )

    totalProcessingTime = sum(
        unbalancedGraph.nodes[k].get('weight') for k in unbalancedGraph.nodes
    )
        

    reportStr.append("----------------------------------------------- Balanced Line -----------------------------------------------")
    reportStr.append("       task groupings                                                     task time               idle time")
    reportStr.append("-------------------------------------------------------------------------------------------------------------")

    res = ["["+"{0:>3}".format(k)+"] "+"{0:<64}"
           .format(str(balancedGraph.nodes[k].get('group')))+"{:12.2f}"
           .format(balancedGraph.nodes[k].get('weight'))+"{:24.2f}"
           .format(metaData['taktTime'] - balancedGraph.nodes[k].get('weight')) for k in balancedGraph.nodes]

    [reportStr.append(f"{res[k]}") for k in range(len(res))]
    addSeparator(reportStr, amount=1)

    reportStr.append("Total idle time                                 : "+"{:12.2f} ".format(float(idleTime)) + metaData['timeUnit'])
    reportStr.append("Smoothness index                                : "+"{:12.2f} ".format(smoothnessIndex))
    reportStr.append(
        "Maximum units with this setup (annual demand)   : " + "{:12.2f}"
        .format(metaData['totalWorkTime'] / max(balancedGraph.nodes[k].get('weight') for k in balancedGraph.nodes))
    )
    reportStr.append("Line efficiency                                 : "+"{:12.2f} %".format( (totalProcessingTime / (float(idleTime) + totalProcessingTime)) * 100))
    

def problemDataToDataFrame(metaData):
    unbalancedGraph = metaData['unBalancedGraph']
    totalProcessingTime = sum(
        unbalancedGraph.nodes[k].get('weight') for k in unbalancedGraph.nodes
    )
    
    data = [
        ["The demand", metaData['demand']],
        [f"Total available time ({metaData['timeUnit']})", metaData['totalWorkTime']],
        [f"The takt time ({metaData['timeUnit']})", metaData['taktTime']],
        [f"The total task time ({metaData['timeUnit']})", totalProcessingTime],
        ["Number of nodes", len(unbalancedGraph.nodes.keys())],
        ["Number of edges", len(unbalancedGraph.edges)],
    ]
    
    df = pd.DataFrame(data, columns=['Assembly line parameters', 'Value'])
    
    st.write("## Problem data")
    st.dataframe(df, use_container_width=True)


def balancedDataToDataFrame(metaData):
    balancedGraph = metaData['balancedGraph']
    unbalancedGraph = metaData['unBalancedGraph']

    idleTime = sum(
        metaData['taktTime'] - balancedGraph.nodes[k].get('weight')
        for k in balancedGraph.nodes
    )

    smoothnessIndex = np.sqrt(
        sum(
            np.power((metaData['taktTime'] - balancedGraph.nodes[k].get('weight')), 2)
            for k in balancedGraph.nodes
        )
    )

    totalProcessingTime = sum(
        unbalancedGraph.nodes[k].get('weight') for k in unbalancedGraph.nodes
    )
    
    data = [
        [
            balancedGraph.nodes[node].get('group'),
            balancedGraph.nodes[node].get('weight'),
            metaData['taktTime'] - balancedGraph.nodes[node].get('weight'),
        ]
        for node in balancedGraph.nodes
    ]
    
    df = pd.DataFrame(data, columns=['Workstation', 'Task time', 'Idle time'])

    st.write("## Balanced assembly line")
    st.write("#### Data")
    st.dataframe(df, use_container_width=True)
    
    metricsData = [
        [f"Total idle time {metaData['timeUnit']}", idleTime],
        ["Smoothness index", smoothnessIndex],
        ["Line efficiency", (totalProcessingTime / (totalProcessingTime + idleTime)) * 100],
    ]
    
    df = pd.DataFrame(metricsData, columns=['Metrics', 'Value'])
    
    st.write('#### Performance')
    st.dataframe(df, use_container_width=True)
    
    
def unbalancedDataToDataFrame(metaData):
    unbalancedGraph = metaData['unBalancedGraph']
    idleTime = sum(
        metaData['taktTime'] - unbalancedGraph.nodes[k].get('weight')
        for k in unbalancedGraph.nodes
    )
    smoothnessIndex = np.sqrt(
        sum(np.power((metaData['taktTime'] - unbalancedGraph.nodes[k].get('weight')), 2,)
            for k in unbalancedGraph.nodes
        )
    )

    totalProcessingTime = sum(
        unbalancedGraph.nodes[k].get('weight') for k in unbalancedGraph.nodes
    )
    
    data = [
        [
            unbalancedGraph.nodes[node].get('name'),
            unbalancedGraph.nodes[node].get('weight'),
            metaData['taktTime'] - unbalancedGraph.nodes[node].get('weight'),
        ]
        for node in unbalancedGraph.nodes
    ]
    
    df = pd.DataFrame(data, columns=['Task name', 'Task time', 'Idle time'])

    st.write("## Unbalanced assembly line")
    st.write("#### Data")
    st.dataframe(df, use_container_width=True)
    
    metricsData = [
        [f"Total idle time {metaData['timeUnit']}", idleTime],
        ["Smoothness index", smoothnessIndex],
        ["Line efficiency", (totalProcessingTime /(totalProcessingTime+idleTime)) * 100],
    ]
    
    df = pd.DataFrame(metricsData, columns=['Metrics', 'Value'])
    
    st.write('#### Performance')
    st.dataframe(df, use_container_width=True)
    