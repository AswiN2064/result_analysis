import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Grade mapping
grade_mapping = {
    'O': 10.0,
    'A+': 9.0,
    'A': 8.0,
    'B+': 7.0,
    'B': 6.0,
    'C': 5.0,
    'U': 0.0,
    'NR': 0.0
}

# Function to create and return the bar chart
def create_bar_chart(df):
    plt.figure(figsize=(8,5))
    sns.barplot(x=df.index.get_level_values('main_exam_code'), y=df['percentage_pass'], palette='coolwarm')
    plt.xlabel('Main Exam Code')
    plt.ylabel('Percentage of Pass (%)')
    plt.title('Percentage of Pass by Main Exam Code')
    plt.xticks(rotation=45)
    plt.ylim(90, 101)
    plt.tight_layout()
    return plt.gcf()

# Function to create and return the pie chart
def create_pie_chart(df):
    passed_students = df['passed_students'].sum()
    total_students = df['total_students'].sum()
    failed_students = total_students - passed_students

    labels = 'Passed', 'Failed'
    sizes = [passed_students, failed_students]
    colors = ['#4CAF50', '#FF6347']  # Green for pass, red for fail

    plt.figure(figsize=(6,6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.axis('equal') 
    plt.title('Pass vs Fail Distribution')
    return plt.gcf()

# Function to assign grades and calculate SGPA and rank
def process_grades(df):
    # Map grades to grade points
    df['grade_point'] = df['grade'].map(grade_mapping)
    
    # Pivot the DataFrame to have one row per reg_no with grades for all subjects
    df_pivot = df.pivot_table(index='reg_no', columns='main_exam_code', values='grade_point', aggfunc='mean')
    
    # Calculate SGPA
    df_pivot['SGPA'] = df_pivot.mean(axis=1)
    
    # Rank based on SGPA, with highest SGPA as rank 1
    df_pivot['Rank'] = df_pivot['SGPA'].rank(ascending=False, method='min').astype(int)
    
    # Include all columns (subjects) in the output
    df_pivot = df_pivot.reset_index()
    
    # Sort by rank to ensure correct ordering
    df_pivot = df_pivot.sort_values(by='Rank')
    
    return df_pivot


# Streamlit app
st.set_page_config(page_title="Exam Results Dashboard", layout="wide")

st.title("Exam Results Dashboard")

# Sidebar for navigation
option = st.sidebar.radio("Select a page:", ["Home", "Grades and Ranks"])

# File uploader
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    # Read the Excel file
    df = pd.read_excel(uploaded_file)
    
    # Rename columns and clean the data
    df = df.rename(
        columns={
            "Unnamed: 0":"reg_no",
            "Unnamed: 1":"student_name",
            "Unnamed: 2":"exam_month",
            "Unnamed: 3":"semester_name",
            "Unnamed: 4":"main_exam_code",
            "Unnamed: 5":"exam_subject_description",
            "Unnamed: 6":"main_exam_name",
            "Unnamed: 7":"credit",
            "Unnamed: 8":"grade_point",
            "Unnamed: 9":"grade",
            "Unnamed: 10":"status"
        }
    )

    df = df.drop(df.index[0])
    df_clean = df.drop(['student_name', 'exam_month', 'semester_name'], axis=1)
    df_clean['status'] = df_clean['status'].apply(lambda x: 1 if x == 'PASS' else 0)

    summary_df = df_clean.groupby(['main_exam_code', 'exam_subject_description']).agg(
        total_students=('reg_no', 'count'),
        passed_students=('status', 'sum')
    )

    summary_df['percentage_pass'] = (summary_df['passed_students'] / summary_df['total_students']) * 100

    # Process grades, SGPA, and rank
    grade_df = process_grades(df)

    # Display based on selected page
    if option == "Home":
        st.subheader("Cleaned Data")
        st.write(df_clean.head())

        st.subheader("Summary Statistics")
        st.write(summary_df)

        st.subheader("Percentage of Pass by Main Exam Code")
        bar_chart = create_bar_chart(summary_df)
        st.pyplot(bar_chart)

        st.subheader("Pass vs Fail Distribution")
        pie_chart = create_pie_chart(summary_df)
        st.pyplot(pie_chart)

    elif option == "Grades and Ranks":
        st.subheader("Student Grades, SGPA, and Ranks")
        st.write(grade_df)

else:
    st.info("Please upload an Excel file to see the results.")
