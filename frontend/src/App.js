import React, { useState } from "react";
import axios from "axios";

function App() {
  const [jd, setJd] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!jd || resumes.length === 0) {
      alert("Please upload JD and resumes");
      return;
    }

    const formData = new FormData();
    formData.append("jd", jd);

    resumes.forEach((file) => {
      formData.append("resumes", file);
    });

    try {
      setLoading(true);
      const response = await axios.post(
        "https://tharuneegonthina-resume-analyzer-api.hf.space/analyze/",
        formData
      );
      setResults(response.data);
    } catch (error) {
      console.error(error);
      alert("Error connecting to backend");
    } finally {
      setLoading(false);
    }
  };

  // 🔥 Download CSV
  const downloadCSV = () => {
    window.open("http://127.0.0.1:8000/download-csv/");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 via-blue-500 to-indigo-600 flex items-center justify-center p-6">

      <div className="bg-white shadow-2xl rounded-3xl p-8 w-full max-w-2xl">

        <h1 className="text-3xl font-bold text-center text-gray-800 mb-6">
          🚀 Resume Analyzer
        </h1>

        {/* JD Upload */}
        <div className="mb-4">
          <label className="block font-semibold text-gray-700 mb-1">
            Upload Job Description
          </label>
          <input
            type="file"
            accept=".txt"
            className="w-full border p-2 rounded-lg"
            onChange={(e) => setJd(e.target.files[0])}
          />
        </div>

        {/* Resume Upload */}
        <div className="mb-4">
          <label className="block font-semibold text-gray-700 mb-1">
            Upload Resumes
          </label>
          <input
            type="file"
            multiple
            accept=".pdf,.docx"
            className="w-full border p-2 rounded-lg"
            onChange={(e) => {
              const filesArray = Array.from(e.target.files);
              setResumes((prev) => [...prev, ...filesArray]);
              e.target.value = null;
            }}
          />
        </div>

        {/* Uploaded Files */}
        <div className="mb-4">
          {resumes.length > 0 && (
            <>
              <h4 className="font-semibold text-gray-700">Uploaded Files:</h4>
              <ul className="text-sm text-gray-600">
                {resumes.map((file, index) => (
                  <li key={index}>📄 {file.name}</li>
                ))}
              </ul>
            </>
          )}
        </div>

        {/* Analyze Button */}
        <button
          onClick={handleSubmit}
          className="w-full bg-gradient-to-r from-purple-500 to-indigo-600 text-white py-2 rounded-lg font-semibold hover:scale-105 transition duration-300"
        >
          {loading ? "Analyzing..." : "Analyze"}
        </button>

        {/* Results */}
        <div className="mt-6">
          {results.length > 0 && (
            <>
              <h2 className="text-xl font-semibold mb-3 text-gray-800">
                Results
              </h2>

              {results.map((item, index) => (
                <div
                  key={index}
                  className="bg-gray-100 p-3 rounded-xl mb-2 flex justify-between items-center"
                >
                  <span>{item["Resume File"]}</span>
                  <span className="font-bold text-purple-600">
                    {(item["Similarity Score"] * 100).toFixed(1)}%
                  </span>
                </div>
              ))}

              {/* 🔥 Download Button */}
              <button
                onClick={downloadCSV}
                className="mt-4 w-full bg-green-500 text-white py-2 rounded-lg hover:bg-green-600"
              >
                Download CSV
              </button>
            </>
          )}
        </div>

      </div>
    </div>
  );
}

export default App;