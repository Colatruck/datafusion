import streamlit as st
import pandas as pd

# 自定义实体匹配算法
def custom_entity_matching(df1, df2, match_columns, drop_columns):
    # 自动检测匹配属性的可选列表
    match_options = list(set(df1.columns) & set(df2.columns))

    if not match_options:
        return None

    # 确保数据集中至少有一条数据
    if len(df1) < 1 or len(df2) < 1:
        return None

    # 获取用户选择的匹配属性
    if not set(match_columns).issubset(match_options):
        return None

    # 根据用户选择的属性进行匹配
    merged_data = pd.merge(df1, df2, on=match_columns, how='outer')  # 使用外连接以保留无法匹配的数据

    return merged_data

# Function to convert DataFrame to CSV for download
def convert_df_to_csv(df):
    return df.to_csv().encode('utf-8')

st.title('IOT数据集成与融合')
st.write('通过实体匹配等算法对数据进行集成与融合')

def load_dataframe(upload):
    if upload is not None:
        if upload.name.endswith('csv'):
            return pd.read_csv(upload, encoding='gbk')  # 指定编码格式为 GBK
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
    st.write("所上传的csv文件2 数据如下:")
    st.dataframe(df2.head())

st.divider()
st.header("数据融合")

if df1_upload is not None and df2_upload is not None:
    if not df1.empty and not df2.empty:
        # 让用户选择用于匹配的属性
        match_columns = st.multiselect("选择用于匹配的属性", options=list(df1.columns))

        # 进行数据融合
        merged_data = custom_entity_matching(df1, df2, match_columns, [])

        if merged_data is not None:
            st.write("融合后的数据如下:")
            st.dataframe(merged_data)

            # 重新检测已生成的融合文件的属性
            merged_columns = list(merged_data.columns)

            # 让用户选择要丢弃的属性
            drop_columns = st.multiselect("选择要丢弃的属性", options=merged_columns)

            # 重新进行数据融合，排除用户选择的属性
            merged_data = merged_data.drop(columns=drop_columns, errors='ignore')

            if not merged_data.empty:
                st.write("经过属性筛选后的融合数据如下:")
                st.dataframe(merged_data)

                # 添加修改后的数据优化模块
                st.header("数据优化")
                if not merged_data.empty:
                    st.write("选择要进行数据优化的属性组:")

                    # 动态添加属性组
                    optimize_attribute_groups = []
                    group_count = st.number_input("选择要优化的属性组数量", min_value=1, max_value=10, value=1)
                    for i in range(group_count):
                        optimize_columns = st.multiselect(f"选择要进行数据优化的属性组 {i + 1}", options=merged_columns)
                        optimize_attribute_groups.append(optimize_columns)

                    # 数据优化逻辑
                    for i, group in enumerate(optimize_attribute_groups):
                        if len(group) == 2:
                            # 为每组设置权重
                            weight = st.slider(f"设置权重 for group {i + 1}", min_value=0.0, max_value=1.0, step=0.01, value=0.5)
                            col1, col2 = group
                            merged_data[f'Optimized_{col1}_{col2}'] = merged_data[col1] * weight + merged_data[col2] * (1 - weight)

                st.write("数据优化后的数据如下:")
                st.dataframe(merged_data)

                # 提供下载按钮
                csv = convert_df_to_csv(merged_data)
                st.download_button(
                    label="下载csv文件",
                    data=csv,
                    file_name='merged_dataframe.csv',
                    mime='text/csv',
                )
            else:
                st.write("所有属性均被丢弃，请重新选择要保留的属性")
        else:
            st.write("未成功融合数据，请重新选择匹配属性")
    else:
        st.write("所上传的数据集是空的，请重新上传")
else:
    st.write("请重新上传")