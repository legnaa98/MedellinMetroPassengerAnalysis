# import modules
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

pd.options.display.float_format = "{:,}".format


class MetroData:
    def __init__(self):
        df_pass = pd.read_csv("./resources/pasajeros_movilizados.csv", sep=";")
        self.df_pass = self.preprocess_data(df_pass)

    def preprocess_data(self, df_pass):
        df_pass = self.rename_cols(df_pass)
        # replace column data types
        df_pass = self.replace_column_types(df_pass)
        return df_pass

    def rename_cols(self, df):
        df_pass = df.copy()
        df_pass.rename(
            columns={
                "L-A_PAX_MOV": "LineA",
                "L-B_PAX_MOV": "LineB",
                "L-K_PAX_MOV": "LineK",
                "L-J_PAX_MOV": "LineJ",
                "L-H_PAX_MOV": "LineH",
                "L-M_PAX_MOV": "LineM",
                "L-L_PAX_MOV": "LineL",
                "L-TA_PAX_MOV": "LineTA",
                "L-1_PAX_MOV": "Line1",
                "L-2_PAX_MOV": "Line2",
                "C-3_PAX_MOV": "LineC3",
                "C6_PAX_MOV": "LineC6",
                "LÍNEA_O": "LineO",
            },
            inplace=True,
        )
        return df_pass

    def replace_column_types(self, df):
        df_pass = df.copy()
        # columns to replace "." to ","
        cols_to_replace = df_pass.columns.values[5:18]
        # convert columns to string
        df_pass[cols_to_replace] = df_pass[cols_to_replace].astype(str)
        # apply the replace function to the strings and then convert into a float again
        for col in cols_to_replace:
            df_pass[col] = df_pass[col].apply(lambda x: float(x.replace(".", "")))
        return df_pass


class EDA:
    def __init__(self):
        df_pass = MetroData().df_pass
        self.lines = df_pass.columns.values[5:18]
        # get passengers for every line on every month
        self.pax_by_month = self.transform_df_month(df_pass, self.lines)
        # get passengers for every line on every semester
        self.pax_by_semester = self.transform_df_sem(df_pass, self.lines)
        # get passengers for every line on every year
        self.pax_by_year = self.transform_df_yr(df_pass, self.lines)

    def transform_df_month(
        self, df_pass: pd.core.frame.DataFrame, lines: np.ndarray
    ) -> pd.core.frame.DataFrame:
        # create empty dataframe to store stacked pax values
        df_transformed = pd.DataFrame([])
        # take line by line and stack the dataframes
        for line in lines:
            # create a copy of the dataframe taking only the number of passengers and the column YearMonth
            df_tmp = df_pass[["AÑO", "NUM_MES", line]].copy()
            df_tmp = df_tmp.dropna()
            df_tmp["YearMonth"] = df_tmp.apply(
                lambda x: str(int(x["AÑO"])) + "-" + str(int(x["NUM_MES"])), axis=1
            )
            # we drop no longer needed columns
            df_tmp.drop(columns=["AÑO", "NUM_MES"], inplace=True)
            # convert yearmonth to date format
            df_tmp["YearMonth"] = pd.to_datetime(df_tmp["YearMonth"], format="%Y-%m")
            # rename the columns in order to have a common name within all steps of for loop
            df_tmp.columns = ["Passengers", "YearMonth"]
            # create new column to assign line label
            df_tmp["Line"] = line
            df_tmp.sort_values(by="YearMonth", ascending=True)
            # fill up the empty dataframe
            df_transformed = pd.concat([df_transformed, df_tmp])

        return df_transformed[["YearMonth", "Passengers", "Line"]]

    def transform_df_sem(
        self, df_pass: pd.core.frame.DataFrame, lines: np.ndarray
    ) -> pd.core.frame.DataFrame:
        # create a copy of the original dataframe
        df = df_pass.copy()
        # groupby semester and summ passenger values by line
        df = df.groupby(["AÑO", "SEMESTRE"], as_index=False)[lines].sum()
        # create column YearSemester
        df["YearSemester"] = df.apply(
            lambda x: str(int(x["AÑO"])) + "-" + str(int(x["SEMESTRE"])), axis=1
        )
        df = df.drop(columns=["SEMESTRE", "AÑO"])
        # empty dataframe to store stacked pax values
        df_transformed = pd.DataFrame([])
        for line in lines:
            df_tmp = df[["YearSemester", line]].copy()
            df_tmp.columns = ["YearSemester", "Passengers"]
            df_tmp["Line"] = line
            df_transformed = pd.concat([df_transformed, df_tmp])
        return df_transformed

    def transform_df_yr(
        self, df_pass: pd.core.frame.DataFrame, lines: np.ndarray
    ) -> pd.core.frame.DataFrame:
        # create a copy of the original dataframe
        df = df_pass.copy()
        # groupby semester and summ passenger values by line
        df = df.groupby(["AÑO"], as_index=False)[lines].sum()
        # rename AÑO column to Year
        df.rename(columns={"AÑO": "Year"}, inplace=True)
        # empty dataframe to store stacked pax values
        df_transformed = pd.DataFrame([])
        for line in lines:
            df_tmp = df[["Year", line]].copy()
            df_tmp.columns = ["Year", "Passengers"]
            df_tmp["Line"] = line
            df_transformed = pd.concat([df_transformed, df_tmp])
        return df_transformed


class ForecastModel:
    def __init__(self):
        self.ticket_hist = pd.read_csv("./resources/ticket_fee.csv")
        # get X and y to fit the linear model
        X = self.ticket_hist[["Year"]].to_numpy()
        y = self.ticket_hist[["Price"]].to_numpy()
        # fit linear model
        lr_model = self.fit_linear_model(X, y)
        # predict ticket prices with the linear model
        self.df_pred = self.linear_model_predict(lr_model)

    def fit_linear_model(self, X, y):
        model = LinearRegression()
        model.fit(X, y)
        return model

    def linear_model_predict(self, model):
        # define years as a numpy array
        x_pred = np.array([2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021])
        # reshape to match sklearn requirements
        x_pred = x_pred.reshape([len(x_pred), 1])
        # compute the ticket fee using the learned model
        y_pred = model.predict(x_pred)
        # create a dataframe with the predicted values
        df_pred = pd.DataFrame(x_pred, columns=["Year"])
        # round off the ticket fees
        df_pred["Price"] = np.round(y_pred, 2)

        return df_pred
