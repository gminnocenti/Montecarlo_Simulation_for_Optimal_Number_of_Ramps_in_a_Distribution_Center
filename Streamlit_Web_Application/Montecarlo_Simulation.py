import pandas as pd
import math 
import random
import streamlit as st
import matplotlib.pyplot as plt

import numpy as np

def VRP(Clientes,Volumen,Matriz_de_tiempo,capacidad,TiempoDeCarga,rampas):

    HorasL = 480 #8 Horas en min
    Rampas = rampas
    Rutas = []
    Rendimientos = []
    end = False
    Numero_camiones = 1
    while end == False:
        T_ClienteMasCercano = 1000000
        ClienteMasCercano = ''
        clientesNovvisitados = []
        Vol_clientesNovvisitados = []
        Ruta = ['Depot']
        Volumen_total = 0
        TiempoTotal = math.ceil((Numero_camiones/Rampas)*TiempoDeCarga) 
        for cliente in range(len(Clientes)):
            c = Clientes[cliente]
            if Matriz_de_tiempo[c]['Depot']<T_ClienteMasCercano:
                T_ClienteMasCercano = Matriz_de_tiempo[c]['Depot']
                v = Volumen[cliente]
                ClienteMasCercano = c
        Ruta.append(ClienteMasCercano)
        TiempoTotal+=T_ClienteMasCercano
        Volumen_total+=v
        for noVisitados in range(len(Clientes)):
            if Clientes[noVisitados] != ClienteMasCercano:
                clientesNovvisitados.append(Clientes[noVisitados])
                Vol_clientesNovvisitados.append(Volumen[noVisitados])
        condiciones = False
        while condiciones == False :
            Origen = Ruta[-1]
            Destinos = []
            for i in range(len(clientesNovvisitados)):
                destino = clientesNovvisitados[i]
                tiempo = Matriz_de_tiempo[destino][Origen]
                regreso = Matriz_de_tiempo['Depot'][destino]
                carga = Vol_clientesNovvisitados[i]
                Destinos.append([destino,tiempo,carga,regreso])
            lista_ordenada = sorted(Destinos, key=lambda x: x[1])
            if lista_ordenada:
                DestinoCercano = lista_ordenada[0][0]
                TiempoaDestino = lista_ordenada[0][1]
                CargaDestino = lista_ordenada[0][2]
                TiempoRegreso = lista_ordenada[0][3]
            else:
                condiciones = True
                continue
            if (TiempoTotal+TiempoaDestino+TiempoRegreso)<=HorasL:
                if CargaDestino+Volumen_total<=capacidad:
                    Ruta.append(DestinoCercano)
                    TiempoTotal+=TiempoaDestino
                    Volumen_total+=CargaDestino
                    RestantesC = []
                    RestantesV = []
                    for x in range(len(lista_ordenada)):
                        if lista_ordenada[x][0]!=DestinoCercano:
                            RestantesC.append(lista_ordenada[x][0])
                            RestantesV.append(lista_ordenada[x][2])
                    clientesNovvisitados = RestantesC
                    Vol_clientesNovvisitados = RestantesV
                    condiciones=False
                else:
                    condiciones=True
            else:
                condiciones=True
        ultimoDestino = Ruta[-1]
        TiempoaBodega = Matriz_de_tiempo['Depot'][ultimoDestino]
        TiempoTotal +=TiempoaBodega
        EspacioNoUtilizado = capacidad-Volumen_total
        TiempoSobrante = HorasL-TiempoTotal
        Rendimiento = [Numero_camiones,TiempoTotal,EspacioNoUtilizado,TiempoSobrante]
        Rendimientos.append(Rendimiento)
        Ruta.append('Depot')
        Rutas.append(Ruta)
        if len(clientesNovvisitados)>0:
            Clientes = clientesNovvisitados
            Volumen = Vol_clientesNovvisitados
            Numero_camiones +=1
            end = False
        else:
            end = True
    columnasRendimiento = ['Ruta','Tiempo total de la ruta','Espacio sobrante del camion','Tiempo sobrante de la ruta']
    df_rendimiento = pd.DataFrame(Rendimientos, columns=columnasRendimiento)
    return Rutas,df_rendimiento,Numero_camiones



def Montecarlo(total_iterations,sample_size,capacidad,TiempoCarga,min_rampas,max_rampas):
 
    iteration_count = 0

    #parametros constantes 
    Clientes = ['Cliente_' + str(i) for i in range(1, sample_size + 1)]
    MaT = pd.read_csv("Matriz_de_tiempo.csv",index_col=0)
    #df con clientes y su volumen total de compra
    df=pd.read_csv('opti_input_VRP.csv')




    means_list = []
    numero_camiones_list=[]
    numero_rampas_list=[]
    numero_clientes_list=[]
    for iteration in range(total_iterations):

        random_clients = df.sample(n=sample_size, random_state=iteration)
            #generar un numero entre 1 y 5 para el numero de rampas
        rampas=random.randint(min_rampas, max_rampas)
        
        # Llamar la funcion del VRP con los nuevos clientes y el nuevo numero de ramoas
        Rutas, Rendimientos,numero_camiones = VRP(Clientes, random_clients['Volumen_Total'].tolist(), MaT, capacidad, TiempoCarga, rampas)
        
        #guardar el promedio de los valores en las diferentes columnas del df Rendimiento en cada itracion
        means = {
            'Mean Time of Route (min)': Rendimientos['Tiempo total de la ruta'].mean(),
            'Mean Leftover Space in Truck (m^3)': Rendimientos['Espacio sobrante del camion'].mean(),
            'Mean Leftover Time (min)': Rendimientos['Tiempo sobrante de la ruta'].mean()
        }
        #guardar la desviacion estandar  de los valores en las diferentes columnas del df Rendimiento en cada itracion

        
        numero_rampas_list.append(rampas)
        numero_camiones_list.append(numero_camiones)
        means_list.append(means)
        numero_clientes_list.append(sample_size)
        
        # Increment the iteration count
        iteration_count += 1

    result_df = pd.DataFrame(means_list)
    result_df["Number of Ramps"] = numero_rampas_list
    result_df["Number of Trucks"] = numero_camiones_list
    result_df["Numero_de_Clientes"] = numero_clientes_list
   



    return result_df

def analyze_dfs(result_df):
    min_values = result_df.groupby(['Number of Ramps', 'Number of Trucks'])[['Mean Leftover Space in Truck (m^3)', 'Mean Time of Route (min)','Mean Leftover Time (min)']].min().reset_index()

    # Next, let's find the row with the overall minimum values for each column
    min_values_min_time = min_values[min_values['Mean Time of Route (min)'] == min_values['Mean Time of Route (min)'].min()]
    min_values_min_space = min_values[min_values['Mean Leftover Space in Truck (m^3)'] == min_values['Mean Leftover Space in Truck (m^3)'].min()]
    min_values_min_leftover_time = min_values[min_values['Mean Leftover Time (min)'] == min_values['Mean Leftover Time (min)'].min()]
    columns_to_drop = [2, 4]
    min_values_min_time = min_values_min_time.drop(min_values_min_time.columns[columns_to_drop], axis=1)
    min_values_min_time = min_values_min_time.reset_index(drop=True)
    columns_to_drop = [3, 4]
    min_values_min_space = min_values_min_space.drop(min_values_min_space.columns[columns_to_drop], axis=1)
    min_values_min_space = min_values_min_space.reset_index(drop=True)    
    columns_to_drop = [2, 3]
    min_values_min_leftover_time = min_values_min_leftover_time.drop(min_values_min_leftover_time.columns[columns_to_drop], axis=1)
    min_values_min_leftover_time = min_values_min_leftover_time.reset_index(drop=True)   
    return min_values_min_time,min_values_min_space,min_values_min_leftover_time

def graphs_dfs(result_df):

    grouped = result_df.groupby(['Number of Ramps', 'Number of Trucks'])

    # Calculate the mean values for the desired columns
    mean_values = grouped[[
        'Mean Time of Route (min)',
        'Mean Leftover Space in Truck (m^3)',
        'Mean Leftover Time (min)'
    ]].mean().reset_index()

    # Create separate bar graphs for each column
    columns_to_plot = [
        'Mean Time of Route (min)',
        'Mean Leftover Space in Truck (m^3)',
        'Mean Leftover Time (min)'
    ]
    listofgraphs=[]
    for column in columns_to_plot:
        # Find the index of the minimum value in the column
        min_value_index = np.argmin(mean_values[column])

        # Create a list of colors, where the bar with the minimum value is green
        colors = ['b' if i == min_value_index else 'r' for i in range(len(mean_values))]

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(
            range(len(mean_values)),
            mean_values[column],
            tick_label=mean_values.apply(lambda row: f"{row['Number of Ramps']} R - {row['Number of Trucks']} T", axis=1),
            color=colors  # Use the colors list to set bar colors
        )
        plt.xlabel('Combination of Ramps and Trucks')
        plt.ylabel(f'{column}')
        plt.title(f'{column} by Combination of Ramps and Cars')
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.show()
        listofgraphs.append(fig)
    
    return listofgraphs


st.set_page_config(
    page_title='Montecarlo Simulation for Optimal Number of Ramps in a Distribution Center',
    layout='wide'
)

st.title('Montecarlo Simulation for Optimal Number of Ramps in a Distribution Center')

st.write('The purpose of this Web Application is to perform a Montecarlo Simulation to find the Optimal Number\
         of Loading Ramps and Trucks for a Distribution Center that has to deliver a maximum of 150 orders daily near the \
         location of the distribution center. The company has a database  of the all the orders made near the location of the distribution center.\
        As part of their strategic planning they want to know the number of loading ramps and trucks needed to minimize route time, leftover space in the trucks, and left over time\
         by the driver. A VRP Algorithm will be running in the backend with the parameters set by the user, and the results of the Montecarlo Simulation,\
         will be displayed at the end of the Application')

st.header('Parameters for Simulation')
total_iterations =int(st.number_input("Enter Number of Iterations for the Montecarlo Simulation: "))
sample_size = st.slider("Select the number of orders you expect to deliver in a day (1-150):", 1, 150, 1)
capacidad = st.number_input("Enter the capacity of the trucks you are expected to use in m^3 ")
TiempoCarga=st.number_input("Enter the time of loading a truck in minutes: ")
min_rampas=int(st.number_input("Enter the Minimun number of Ramps you expect to use : "))
max_rampas=int(st.number_input("Enter the Maximum number of Ramps you expect to use : "))




#call montecarlo function
# Create a Streamlit button
if st.button("Execute Montecarlo Simulation"):
    st.header('Results of Simulation')
    result_df=Montecarlo(total_iterations,sample_size,capacidad,TiempoCarga,min_rampas,max_rampas)
#call analyse_dfs function
    min_values_min_time, min_values_min_space, min_values_min_leftover_time = analyze_dfs(result_df)
#call graphs_dfs function
    listofgraphs=graphs_dfs(result_df)
    #start the display
    st.subheader("Best combination of Trucks and Ramps for minimizing route time: ")
    st.write(min_values_min_time)
    st.pyplot(listofgraphs[0])

    st.subheader("Best combination of Trucks and Ramps for minimizing left over space in the trucks: ")
    st.write(min_values_min_space)
    st.pyplot(listofgraphs[1])
    st.subheader("Best combination of Trucks and Ramps for minimizing left over time: ")
    st.write(min_values_min_leftover_time)
    st.pyplot(listofgraphs[2])

    