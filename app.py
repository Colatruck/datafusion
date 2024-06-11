import streamlit as st
import pandas as pd
import numpy as np
from valentine import valentine_match
from valentine.algorithms import Coma


# Function to convert DataFrame to CSV for download
def convert_df_to_csv(df):
    return df.to_csv().encode('utf-8')


st.title('IOT数据集成与融合')
st.write('通过实体匹配等算法对数据进行集成与融合')


def load_dataframe(upload):
    if upload is not None:
        if upload.name.endswith('csv'):
            return pd.read_csv(upload)
        else:
            return pd.read_excel(upload)
    else:
        return pd.DataFrame()


st.divider()
st.header("上传数据")

# 上传第一个数据
df1_upload = st.file_uploader("上传物联网数据 CSV文件", type=['csv'], key='df1_upload')

df1 = load_dataframe(df1_upload)
if df1 is not None:
    st.write("所上传的csv文件1 数据如下:")
    st.dataframe(df1.head())

# 上传第二个数据
df2_upload = st.file_uploader("上传物联网数据 CSV文件", type=['csv'], key='df2_upload')

df2 = load_dataframe(df2_upload)

if df2 is not None:
    st.write("所上传的csv文件1 数据如下:")
    st.dataframe(df2.head())

st.divider()
st.header("数据融合")

if df1_upload is not None and df2_upload is not None:
    if not df1.empty and not df2.empty:
        # 进行实体匹配，获取两个数据集所匹配到的实体
        st.subheader("实体匹配")

        st.write("请选择实体匹配的权重")
        weight = st.slider("权重", 0.0, 1.0, 0.5)

        match_col = []

        # 进行实体匹配算法

        matcher = Coma(use_instances=True)
        matches = valentine_match(df1, df2, matcher)
        for match in matches:
            if matches[match] > weight:
                match_col.append((match[0][1], match[1][1]))

        if match_col:
            default_value = match_col  # 使用第一个元素作为默认值
        else:
            default_value = None  # 如果 match_col 为空，则默认值为 None

        # 使用默认值（如果 match_col 不为空，则设置为第一个元素，否则为 None）
        selected_match_col = st.multiselect(
            "选择所匹配到的实体列",
            options=match_col,
            default=default_value
        )

        st.divider()

        # 数据融合
        if st.button("融合数据"):
            st.subheader("数据融合")

            fused_records = []

            all_rows = pd.concat([df1, df2], ignore_index=True)

            for idx in range(len(all_rows)):
                if idx < len(df1):
                    r1 = df1.iloc[idx]
                    r2 = None
                else:
                    r1 = None
                    r2 = df2.iloc[idx - len(df1)]

                fused_record = {}

                for col1, col2 in selected_match_col:
                    if r1 is not None and col1 in r1:
                        fused_record[col1] = r1[col1]
                    elif r2 is not None and col2 in r2:
                        fused_record[col1] = r2[col2]
                    else:
                        fused_record[col1] = None

                unmatched_cols1 = [col for col in df1.columns if col not in dict(selected_match_col).keys()]
                unmatched_cols2 = [col for col in df2.columns if col not in dict(selected_match_col).values()]

                for col in unmatched_cols1:
                    fused_record[col] = r1[col] if r1 is not None else None
                for col in unmatched_cols2:
                    fused_record[col] = r2[col] if r2 is not None else None

                fused_records.append(fused_record)

            final_fused_df = pd.DataFrame(fused_records)

            st.write("融合后的数据如下:")
            st.dataframe(final_fused_df.head())

            csv = convert_df_to_csv(final_fused_df)
            st.download_button(
                label="下载csv文件",
                data=csv,
                file_name='merged_dataframe.csv',
                mime='text/csv',
            )

    else:
        st.write("所上传的数据集是空的，请重新上传")
else:
    st.write("请重新上传")
