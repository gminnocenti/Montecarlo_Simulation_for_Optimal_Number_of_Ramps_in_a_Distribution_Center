# Montecarlo_Simulation_for_Optimal_Number_of_Ramps_in_a_Distribution_Center

A Logistics company has but a new plot of land for a Distribution Center in a new area where they've experienced a surge in operations. Before they start building their new Distribution Center they wish to know the optimal number of Ramps and Trucks to minimize route time, left over space in the trucks, and leftover time by the trucks. The company will provide a historical dataset with past orders, and with 150 directions of the most common delivery addresses.

# Solution 
For this you will need to simulate costumer orders based on relative frequency to find how many products each client will buy. After simulating the number of products you will need to simulate which products the clients will buy with the same methodology. You can find this Data Processing in the Data_Processing Folder. After you generate the costumer Orders you will implement a VRP ALgorithm a n number of times with the Web Application you can find in the Streamlit_Web_Application Folder where the Simulation will execute on the backend and give you an Analysis based on the parameters given by the user.

