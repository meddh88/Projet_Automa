import './App.css';
import { useState } from 'react';
import * as XLSX from 'xlsx';

function App() {
  //onchange states
  const [Excelfile, setExcelFile] = useState(null);
  const [typeError, setTypeError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSMULoading, setIsSMULoading] = useState(false);
  const [isSmartScanLoading, setIsSmartScanLoading] = useState(false);

  //submit states
  const [Exceldata, setData] = useState(null);

  // Fonction de filtrage des données
  const filteredData = Exceldata
    ? Exceldata.filter(row =>
        Object.values(row).some(value =>
          value.toString().toLowerCase().includes(searchQuery.toLowerCase())
        )
      )
    : null;

  //onchange event
  const handleFile = (e) => {
    let fileType = ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','text/csv'];
    let selectedFile = e.target.files[0];
    
    if (selectedFile) {
      if(fileType.includes(selectedFile.type)) {
        setTypeError(null);
        let reader = new FileReader();
        reader.readAsArrayBuffer(selectedFile);
        reader.onload = (e) => {
          setExcelFile(e.target.result);
        };
      } else {
        setTypeError('Please select only excel file types');
        setExcelFile(null);
      }
    } else {
      console.log('Please select your file');
    }
  };


  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      if(Excelfile !== null) {
        // Simuler un délai pour voir le loading
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        const workbook = XLSX.read(Excelfile, {type: 'buffer'});
        const worksheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[worksheetName];
        const data = XLSX.utils.sheet_to_json(worksheet);
        setData(data);
      }
    } catch (error) {
      console.error('Error processing file:', error);
      setTypeError('Error processing the file');
    } finally {
      setIsLoading(false);
    }
  }
   
  
  // Fonction pour exporter les données filtrées
  const handleExport = () => {
    if (filteredData) {
      const ws = XLSX.utils.json_to_sheet(filteredData);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, "Données Filtrées");
      XLSX.writeFile(wb, "données_filtrées.xlsx");
    }
  };

  // Fonction pour l'exportation vers l'application SMU
  const handleSMUExport = async () => {
    if (!Excelfile) {
      alert('Please upload a file first!');
      return;
    }

    try {
      setIsSMULoading(true);
      console.log('Starting export process...');
      
      // Get the file from the input element
      const fileInput = document.querySelector('input[type="file"]');
      if (!fileInput || !fileInput.files[0]) {
        alert('No file selected');
        return;
      }
      
      // Verify file type
      const file = fileInput.files[0];
      const validTypes = ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv'];
      if (!validTypes.includes(file.type)) {
        alert('Please select a valid Excel file (.xls, .xlsx, or .csv)');
        return;
      }

      // Create a form data object to send the file
      const formData = new FormData();
      formData.append('file', file);
      
      console.log('Preparing to send file:', file.name);

      // Test server connection
      console.log('Testing server connection...');
      try {
        const testResponse = await fetch('http://localhost:3001/test', {
          method: 'GET',
          mode: 'cors',
          headers: {
            'Accept': 'application/json'
          }
        });
        
        if (!testResponse.ok) {
          throw new Error('Server test failed');
        }
        
        const testData = await testResponse.json();
        console.log('Server test response:', testData);
      } catch (e) {
        console.error('Server connection test failed:', e);
        throw new Error('Could not connect to server. Please make sure the Flask server is running on port 3001.');
      }

      console.log('Server is running, sending file...');
      const apiUrl = 'http://localhost:3001/api/smu-export';
      console.log('Sending file to:', apiUrl);
      const response = await fetch(apiUrl, {
        method: 'POST',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
        body: formData
      });

      if (!response.ok) {
        let errorMessage;
        try {
          const errorData = await response.json();
          errorMessage = errorData.error || 'Export failed';
        } catch (e) {
          errorMessage = `Server error (${response.status}): ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      alert(data.message);
      
      // Si l'export a réussi, ouvrir le dossier
      if (data.openFolder) {
        window.open('file:///C:/Exam_GRP_SMUAPP', '_blank');
      }

    } catch (error) {
      console.error('Error during export:', error);
      if (error.message === 'Failed to fetch') {
        alert('Unable to connect to the server. Please make sure the server is running on port 3001 and try again.');
      } else {
        alert('Error during export: ' + error.message);
      }
    } finally {
      setIsSMULoading(false);
    }
  };

  // Fonction pour générer le fichier Smart Scan
  const handleSmartScanGenerate = async () => {
    if (!Excelfile) {
      alert('Please upload a file first!');
      return;
    }

    try {
      setIsSmartScanLoading(true);
      console.log('Starting Smart Scan export process...');
      
      const fileInput = document.querySelector('input[type="file"]');
      if (!fileInput || !fileInput.files[0]) {
        alert('No file selected');
        return;
      }
      
      const file = fileInput.files[0];
      const validTypes = ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv'];
      if (!validTypes.includes(file.type)) {
        alert('Please select a valid Excel file (.xls, .xlsx, or .csv)');
        return;
      }

      const formData = new FormData();
      formData.append('file', file);
      
      console.log('Preparing to send file:', file.name);

      // Test server connection first
      try {
        const testResponse = await fetch('http://localhost:3001/test');
        if (!testResponse.ok) throw new Error('Server test failed');
      } catch (e) {
        throw new Error('Could not connect to server. Please make sure the Flask server is running on port 3001.');
      }

      const response = await fetch('http://localhost:3001/api/smart-scan-export', {
        method: 'POST',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Smart Scan export failed');
      }

      const data = await response.json();
      alert(data.message);

    } catch (error) {
      console.error('Error during Smart Scan export:', error);
      if (error.message === 'Failed to fetch') {
        alert('Unable to connect to the server. Please make sure the server is running on port 3001 and try again.');
      } else {
        alert('Error during Smart Scan export: ' + error.message);
      }
    } finally {
      setIsSmartScanLoading(false);
    }
  };

  //read data from excel file
  return (
    <div className="wrapper">
      {isLoading && (
        <div className="loading-overlay">
          <div className="dots-loading">
            <div className="dot"></div>
            <div className="dot"></div>
            <div className="dot"></div>
            <div className="dot"></div>
          </div>
          <div className="loading-text">
            Loading<span className="dot-one">.</span><span className="dot-two">.</span><span className="dot-three">.</span>
          </div>
        </div>
      )}
      <h3>Upload, View & Separate Excel Sheets</h3>
      
      <form className="form-group custom-form" onSubmit={handleSubmit}>
        <input type="file" className="form-control" onChange={handleFile} disabled={isLoading} />
        <button type="submit" className="btn btn-success btn-with-spinner" disabled={isLoading}>
          UPLOAD <span className="download-arrow">↑</span>
        </button>
        {typeError && (
          <div className="alert alert-danger" role='alert'>{typeError}</div>
        )}
      </form>

      <div className="viewer">
        {Exceldata ? (
          <div>
            <div className="stats-info">
              <p>Nombre de lignes : {Exceldata.length}</p>
              <p>Nombre de colonnes : {Object.keys(Exceldata[0]).length}</p>
            </div>
            <div className="export-buttons">
              <button 
                className={`btn btn-smu ${isSMULoading ? 'loading' : ''}`} 
                onClick={() => handleSMUExport()}
                disabled={isSMULoading}
              >
                {isSMULoading ? 'Processing...' : 'Export to SMU App'} <span className="export-icon">📱</span>
              </button>
              <button 
                className={`btn btn-smart-scan ${isSmartScanLoading ? 'loading' : ''}`} 
                onClick={() => handleSmartScanGenerate()}
                disabled={isSmartScanLoading}
              >
                {isSmartScanLoading ? 'Processing...' : 'Export to Smart Scan'} <span className="export-icon">⚡</span>
              </button>
            </div>
            <div className="search-container">
              <input
                type="text"
                className="search-input"
                placeholder="Rechercher dans le tableau..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button className="btn btn-export" onClick={handleExport}>
                Exporter <span className="download-arrow">↓</span>
              </button>
            </div>
            <div className="table-responsive">
              <table className="table">
                <thead>
                  <tr>
                    {Object.keys(Exceldata[0]).map((key) => (
                      <th key={key}>{key}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {filteredData.map((row, rowIndex) => (
                    <tr key={rowIndex}>
                      {Object.entries(row).map(([key, cell], colIndex) => (
                        <td 
                          key={colIndex}
                          data-row={rowIndex + 1}
                          data-col={colIndex + 1}
                        >
                          {cell}
                          <span className="tooltip">
                            Ligne {rowIndex + 1}, Colonne {colIndex + 1}
                          </span>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="no-file">No File is uploaded yet!</div>
        )}
      </div>
    </div>
  );
}

export default App;
