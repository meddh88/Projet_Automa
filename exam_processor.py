import shutil
import pandas as pd
import os
import sys

def separate_exam_by_day(input_file):
    """
    Processes the exam file to create a structured directory organization:
    - Creates main directory 'Exam_GRP_SMUAPP'
    - Creates subdirectories for each course
    - Creates separated group files in CSV format with Student ID, Email, and GroupEXM
    
    Args:
        input_file (str): Path to the input Excel file
        
    Returns:
        tuple: (bool, str) - (Success status, Message)
    """
    try:
        print(f"Lecture du fichier: {input_file}")
        
        # Validate file existence
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Le fichier {input_file} n'existe pas")
            
        # Read the Excel file
        df = pd.read_excel(input_file)
        print("Fichier Excel lu avec succes")
        
        # Validate required columns
        required_columns = ['Course Title', 'GroupEXM', 'Student ID', 'Email']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Colonnes manquantes dans le fichier: {', '.join(missing_columns)}")
        
        # Create main output directory
        main_dir = r'C:\Exam_GRP_SMUAPP'
        if not os.path.exists(main_dir):
            os.makedirs(main_dir)
            print(f"Dossier principal cree: {main_dir}")

        # Initialize counters
        course_count = 0
        group_count = 0
        
        # Process each unique course
        for course in df['Course Title'].unique():
            try:
                # Clean course name for folder name
                course_clean = str(course).strip().replace(" ", "_").replace("/", "-")
                
                # Create course directory
                course_dir = os.path.join(main_dir, course_clean)
                if not os.path.exists(course_dir):
                    os.makedirs(course_dir)
                
                # Get data for this course
                course_data = df[df['Course Title'] == course]
                
                # Save full course file
                course_file = os.path.join(course_dir, f"{course_clean}.xlsx")
                with pd.ExcelWriter(course_file, engine='openpyxl') as writer:
                    course_data.to_excel(writer, index=False)
                print(f"Fichier cours cree: {course_file}")
                
                # Create groups directory
                groups_dir = os.path.join(course_dir, f"{course_clean}_GRP_separated")
                if not os.path.exists(groups_dir):
                    os.makedirs(groups_dir)
                
                # Create separate files for each group
                for group in course_data['GroupEXM'].unique():
                    group_data = course_data[course_data['GroupEXM'] == group]
                    group_clean = str(group).strip().replace(" ", "_").replace("/", "-")
                    
                    # Format file name as Course_Title_groupe
                    group_file = os.path.join(groups_dir, f"{course_clean}_groupe{group_clean}.csv")
                    
                    # Save group data with specific columns
                    selected_columns = ['Student ID', 'Email', 'GroupEXM']
                    group_data[selected_columns].to_csv(group_file, index=False)
                    print(f"Fichier groupe cree: {group_file}")
                    group_count += 1
                
                course_count += 1
                
            except Exception as e:
                print(f"Erreur lors du traitement du cours {course}: {str(e)}")
                continue
        
        # Return success message with statistics
        message = f"Traitement termine avec succes. {course_count} cours traites, {group_count} fichiers groupes crees."
        return True, message
            
    except FileNotFoundError as e:
        return False, f"Erreur: {str(e)}"
    except ValueError as e:
        return False, f"Erreur de format: {str(e)}"
    except Exception as e:
        return False, f"Une erreur inattendue s'est produite: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python exam_processor.py <input_file_path>")
        print("Example: python exam_processor.py data.xlsx")
        sys.exit(1)
    
    input_file = sys.argv[1]
    success, message = separate_exam_by_day(input_file)
    print(message)
    if not success:
        sys.exit(1)
