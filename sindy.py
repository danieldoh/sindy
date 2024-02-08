import numpy as np
import argparse
import itertools
import math
import os
import sklearn
import datetime
import pandas as pd
from sklearn import metrics
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt


def create_plt_folder():
    current_datetime = datetime.datetime.now()
    date_str = current_datetime.strftime("%Y-%m-%d_%H-%M")

    folder_path = os.path.join(os.getcwd(), date_str)
    os.makedirs(folder_path, exist_ok=True)


def distribution(data, variable_list, folder_path):
    # Histogram before log transformation

    for i, variable in enumerate(variable_list):
        plt.figure(i)
        fig, axs = plt.subplots(2, 2, figsize=(16, 8))
        axs[0, 0].hist(data[variable], bins=30, edgecolor='black')
        axs[0, 0].set_xlabel(variable)
        axs[0, 0].set_ylabel("Frequency")
        axs[0, 0].set_title("Histogram of Original data")

        # Normal distribution before log transformation
        mean_b = data[variable].mean()
        std_b = data[variable].std()
        x1 = np.linspace(data[variable].min(), data[variable].max(), 100)
        y1 = (1 / (std_b * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x1 - mean_b) / std_b) ** 2)
        axs[0, 1].plot(x1, y1, color='blue')
        axs[0, 1].set_xlabel(variable)
        axs[0, 1].set_ylabel('Probability Density')
        axs[0, 1].set_title('Normal Distribution of Original Data')

        # Histogram after log transformation
        data[variable] = data[variable].apply(np.log1p)
        axs[1, 0].hist(data[variable], bins=30, edgecolor='black')
        axs[1, 0].set_xlabel(variable)
        axs[1, 0].set_ylabel("Frequency")
        axs[1, 0].set_title("Histogram after Log Transformation")

        mean_a = data[variable].mean()
        std_a = data[variable].std()
        x2 = np.linspace(data[variable].min(), data[variable].max(), 100)
        y2 = (1 / (std_a * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x2 - mean_a) / std_a) ** 2)
        axs[1, 1].plot(x2, y2, color='blue')
        axs[1, 1].set_xlabel(variable)
        axs[1, 1].set_ylabel("Probability Density")
        axs[1, 1].set_title("Normal Distribution after Log Transformation")
        plt.tight_layout()
        save_path = os.path.join(folder_path, f"{variable}_distribution.png")
        plt.savefig(save_path)

def log_transformation(data):
	data = data.apply(np.log1p)
	return(data)

def standardization(data):
    scaler = StandardScaler()
    cols = data.columns
    for col in cols:
        data[[col]] = scaler.fit_transform(data[[col]])
    return(data)

#이건 뒤에 마지막 3개 함수에 사용되기만 하고 직접 사용자한테 보여줄(?) 필요는 없는 함수야~~~~~~~~~~~


def get_polynomial_combinations(inputdata, order):
    poly_cols = []
    for cur_order in range(1, order + 1):
        for col_comb in itertools.combinations_with_replacement(inputdata.columns, cur_order):
            poly_col = inputdata[list(col_comb)].product(axis=1)
            col_name = '*'.join(col_comb)
            poly_col.name = col_name
            poly_cols.append(poly_col)
    poly_df = pd.concat(poly_cols, axis=1)
    poly_df.insert(0, 'constant', 1)
    return poly_df

#이것도 다른 함수에 사용되기만 하는거야~~~~~~~~~~

def stls(target, library, threshold_value):
    lib = library.copy()
    kss = []
    for i in range(20):
        library_inverse = pd.DataFrame(np.linalg.pinv(lib))
        ksi = library_inverse.values @ target.values
        ksi = pd.DataFrame(ksi)
        ksi[abs(ksi) < threshold_value] = 0
        ind = ksi[ksi == 0].stack().index.get_level_values(0).tolist()
        lib_updated = lib.copy()
        lib_updated[lib_updated.columns[ind]] = 0
        kss.append(ksi)
        lib = lib_updated
    return kss[19]

# threshold value 를 0으로 놓고(=STLS과정이 한 번만 있으면 된다는 뜻)
# 라이브러리 행렬과 크시 벡터의 곱을 해서 나온 결과의 MSE, AIC분석
def polynomialorder(inputdata, target, ordernum, folder_path):
    aic = []
    mse = []
    order = []
    term = []
    for i in range(1,ordernum+1):
        lib = get_polynomial_combinations(inputdata, i)
        library_inverse = pd.DataFrame(np.linalg.pinv(lib))
        ksi = library_inverse.values@target.values
        ksi = pd.DataFrame(ksi)
        result = lib.values@ksi.values
        ms = sklearn.metrics.mean_squared_error(target, result)
        mse.append(ms)
        n = len(inputdata)
        K = sum((ksi != 0).sum())
        #K is parameter, which is the number of nonzero ksi vector values.
        ai = n*math.log(ms) + 2*K + (2*K*(K+1))/(n-K-1)
        aic.append(ai)
        term.append(K)
        order.append(i)
    fig, axs = plt.subplots(3, 1, figsize=(6, 8), gridspec_kw={'height_ratios': [2, 2, 2]})
    axs[0].plot(order, term)
    axs[0].set_xlabel("Polynomial order")
    axs[0].set_ylabel("Term number")
    axs[1].plot(order, mse)
    axs[1].set_xlabel("Polynomial order")
    axs[1].set_ylabel("MSE")
    axs[2].plot(order, aic)
    axs[2].set_xlabel("Polynomial order")
    axs[2].set_ylabel("AICc")
    fig.subplots_adjust(hspace=1)
    save_path = os.path.join(folder_path, "polynomial.png")
    plt.savefig(save_path)
    #plt.show()

def thresholdvalue(inputdata, target, order, start, end, folder_path):
    library = get_polynomial_combinations(inputdata, order)
    my_array = np.arange(start, end, (end - start) / 100)
    aic = []
    empty_aic = []
    mse = []
    empty_mse = []
    term = []
    empty_term = []
    array = []
    empty_array = []


    for value in my_array:
        ksi = stls(target, library, value)
        result = library.values @ ksi.values
        ms = sklearn.metrics.mean_squared_error(target, result)
        n = len(inputdata)
        K = sum((ksi != 0).sum())
        if n - K - 1 != 0:  # Exclude points where the denominator is zero
            logms = math.log(ms)
            ai = n * logms + 2 * K + (2 * K * (K + 1)) / (n - K - 1)
            aic.append(ai)
            term.append(K)
            mse.append(ms)
            array.append(value)
        else:
            empty_array.append(value)
            empty_aic.append(0)
            empty_mse.append(0)
            empty_term.append(0)

    sorted_aicdata = sorted(zip(array + empty_array, aic + empty_aic), key=lambda data: data[0])
    array_combined, aic_combined = zip(*sorted_aicdata)
    sorted_msedata = sorted(zip(array + empty_array, mse + empty_mse), key=lambda data: data[0])
    array_combined, mse_combined = zip(*sorted_msedata)
    sorted_termdata = sorted(zip(array + empty_array, term + empty_term), key=lambda data: data[0])
    array_combined, term_combined = zip(*sorted_termdata)

    fig, axs = plt.subplots(3, 1, figsize=(5, 10), gridspec_kw={'height_ratios': [2, 2, 2]})
    axs[0].plot(array_combined, term_combined)
    axs[0].set_xlabel("threshold value")
    axs[0].set_ylabel("term")
    axs[1].plot(array_combined, mse_combined)
    axs[1].set_xlabel("threshold value")
    axs[1].set_ylabel("MSE")
    axs[2].plot(array_combined, aic_combined)
    axs[2].set_xlabel("threshold value")
    axs[2].set_ylabel("AICc")

    for i in range(len(empty_array) - 1):
        axs[2].fill_betweenx([min(aic_combined), max(aic_combined)], empty_array[i], empty_array[i + 1], color='gray', alpha=0.5)

    fig.subplots_adjust(hspace=0.7)
    save_path = os.path.join(folder_path, "threshold_value.png")
    plt.savefig(save_path)
    #plt.show()

def result(inputdata, target, order, lamb, folder_path):
    library = get_polynomial_combinations(inputdata, order)
    ksi = stls(target, library, lamb)
    term = sum((ksi!= 0).sum())
    ksi_tf = (ksi!=0)
    ind = ksi_tf[ksi_tf.iloc[:, 0]].index
    variable_list = list(library.iloc[:,ind].columns)
    ksi_list = ksi.iloc[:,0][ksi.iloc[:,0] != 0].tolist()
    abs_values = [abs(x) for x in ksi_list]
    result = pd.DataFrame({'Variables': variable_list, 'Value': ksi_list,'Weighted Value': abs_values})
    result = result.sort_values('Weighted Value', ascending=False)

    import numpy as np
    res = library.values@ksi.values
    target_name = target.columns[0]
    target = np.array(target)
    correlation_coefficient = np.corrcoef(target.flatten(), res.flatten())[0, 1]


    variable = list(result["Variables"])
    weighted = list(result["Weighted Value"])
    x=range(len(variable))

    # Create the scatter plot
    fig,axes = plt.subplots(2,1, figsize = (3,8))
    axes[0].scatter(res,target)
    axes[0].set_xlabel('Model Result')
    axes[0].set_ylabel('Target')
    axes[0].set_title('Scatter Plot')
    axes[1].bar(x, weighted, color = "skyblue")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(variable, rotation = 90)
    axes[1].set_xlabel('Variables')
    axes[1].set_ylabel('Weighted Value')

    #plt.grid(True)
    plt.tight_layout()
    save_path = os.path.join(folder_path, "result.png")
    plt.savefig(save_path)
    #plt.show()

    expression_parts = []
    for index, row in result.iterrows():
        expression_part = f"({row['Value']})*{row['Variables']}"
        expression_parts.append(expression_part)

    expression = f"{target_name} = " + " + ".join(expression_parts)

    print('Correlation Coefficient:', round(correlation_coefficient,2))
    print('Threshold value:',lamb)
    print('Term:',term)
    print(expression)
    return result, round(correlation_coefficient,2), lamb, term, expression

def get_data(file_path):
    df = pd.read_csv(file_path)
    return df

if __name__ == "__main__":

    create_plt_folder()

    parser = argparse.ArgumentParser(description='sindy argparse')
    parser.add_argument('--file_path', help='insert csv file path')
    args = parser.parse_args()

    data = get_data(args.file_path)

    variable_list = data.columns.tolist()
    #print(variable_list)
    #distribution(data, variable_list)

    log_transformation_check = input("Want to apply log [y/n]: ")
    if log_transformation_check == "y" or log_transformation_check == "Y":
        data = log_transformation(data)
        print(data)
    else:
        print("Log is not applied.")

    # standardized
    data = standardization(data)
    print("Standardized...")

    # polynomial order
    print("These are columns:")
    print(data)
    variable_list = data.columns.tolist()
    target_column = input("Choose Target Column [예시- CFU]: ")
    target = data[[target_column]]
    input_data = data.drop([target_column], axis=1)

    print("Current Columns:")
    print(input_data)
    want_to_drop = input("Want to drop more columns [y/n]: ")

    while want_to_drop == "y" or want_to_drop == "Y":
        drop_column = input("Choose a Column to drop:")
        input_data = input_data.drop([drop_column], axis=1)
        print("Current Columns:")
        print(input_data)
        want_to_drop = input("Wnat to drop more columns [y/n]: ")

    ordernum = int(input("Write the order number (suggestion=6): "))
    polynomialorder(input_data, target, ordernum)

    order = int(input("Write the proper order number: "))
    start = int(input("Write the start number: "))
    end = int(input("Write the end number: "))

    thresholdvalue(input_data, target, order, start, end)

    want_to_get_result = input("Want to get result [y/n]: ")
    lamb = float(input("Write the initial threshold value: "))

    while want_to_get_result == "y" or want_to_get_result == "Y":
        result(input_data, target, order, lamb)
        want_to_get_result = input("Want to get more result [y/n]: ")

        if (want_to_get_result != "y" and want_to_get_result != "Y"):
            break

        lamb = float(input("Write the threshold value: "))


