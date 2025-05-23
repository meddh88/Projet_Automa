import shutil
import pandas as pd
import os
import sys

def separate_exam_by_day(input_file):
    try:
        # Read the Excel file
        df = pd.read_excel(input_file)
        
        # Print all column names and unique values in DAY column
        print("Colonnes disponibles:", df.columns.tolist())
        print("Valeurs uniques dans la colonne DAY:", df['DAY'].unique().tolist())

        # Create output directory in C: drive
        output_dir = r'C:\Exam_DAY_Smart'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        print("Dossier cree avec succes vers : C:\\Exam_DAY_Smart")

        # Directly use the DAY column since we know it exists
        for jour, sous_df in df.groupby('DAY'):
            # Clean the day name (remove spaces and special characters)
            nom_jour = str(jour).strip().replace(" ", "_")
            nom_fichier = os.path.join(output_dir, f"Jour_{nom_jour}.xlsx")
            
            # Save to Excel file
            with pd.ExcelWriter(nom_fichier, engine='openpyxl') as writer:
                sous_df.to_excel(writer, index=False)
            print(f"Fichier cree : {nom_fichier}")
        
        return True, "Traitement termine avec succes"
    
    except Exception as e:
        error_message = str(e)
        print(f"Erreur: {error_message}")
        return False, f"Erreur lors du traitement: {error_message}"

if __name__ == '__main__':
    # For testing purposes only
    if len(sys.argv) > 1:
        separate_exam_by_day(sys.argv[1])
    else:
        print("Veuillez fournir un chemin de fichier en entrée")