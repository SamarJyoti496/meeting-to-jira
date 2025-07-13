import { useCallback, useState } from "react";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [projectKey, setProjectKey] = useState("PROJ");
  const [assignee, setAssignee] = useState("");
  const [status, setStatus] = useState({ message: "", type: "" });
  const [progress, setProgress] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [tickets, setTickets] = useState([]);

  const handleFileSelect = (event) => {
    if (event.target.files && event.target.files.length > 0) {
      console.log(event);
      setSelectedFile(event.target.files?.[0]);
      setStatus({ message: "", type: "" });
      setTickets([]);
    }
  };

  const showStatus = (message, type) => {
    setStatus({ message, type });
  };

  const pollStatus = useCallback(async (meetingId) => {
    try {
      const response = await fetch(`/api/v1/meetings/${meetingId}/status`);
      const data = await response.json();

      console.log(data);
      if (!response.ok) throw new Error(data.detail || "Failed to get status");

      setProgress(data.progress);
      showStatus(data.message, "info");

      if (data.status === "completed") {
        showStatus("Processing Complete! 🎉", "success");
        setIsProcessing(false);
        const ticketsResponse = await fetch(
          `/api/v1/meetings/${meetingId}/tickets`
        );
        const ticketsData = await ticketsResponse.json();
        setTickets(ticketsData.tickets || []);
      } else if (data.status === "failed") {
        showStatus(`Processing failed: ${data.message}`, "error");
        setIsProcessing(false);
      } else {
        setTimeout(() => pollStatus(meetingId), 3000);
      }
    } catch (error) {
      showStatus(`Status check failed: ${error.message}`, "error");
      setIsProcessing(false);
    }
  }, []);

  const handleUpload = async () => {
    if (!selectedFile) return showStatus("Please select a file first", "error");
    if (!projectKey)
      return showStatus("Please enter a Jira Project Key", "error");

    const formData = new FormData();
    formData.append("file", selectedFile);

    setIsProcessing(true);
    setProgress(0);
    setTickets([]);
    showStatus("Uploading file....", "info");

    try {
      const response = await fetch(
        `/api/v1/upload?project_key=${projectKey}&assignee=${assignee || ""}`,
        {
          method: "POST",
          body: formData,
        }
      );

      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || "Upload failed");

      showStatus("File uploaded. Starting process... ⚙️", "success");
      pollStatus(result.meeting_id);
    } catch (error) {
      showStatus(`Error: ${error.message}`, "error");
      setIsProcessing(false);
    }
  };

  const statusStyles = {
    success: "bg-emerald-50 border-emerald-200 text-emerald-800",
    error: "bg-red-50 border-red-200 text-red-800",
    info: "bg-blue-50 border-blue-200 text-blue-800",
  };

  return (
    <div className="bg-gradient-to-br from-slate-50 to-blue-50 min-h-screen py-10">
      <div className="max-w-4xl mx-auto bg-white shadow-2xl rounded-2xl overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 py-12 px-8 text-center">
          <h1 className="text-4xl font-bold text-white mb-3">
            Meeting to Jira Converter
          </h1>
          <p className="text-xl text-blue-100">
            Effortlessly transform meeting recordings into Jira tasks.
          </p>
        </div>

        <div className="p-8 space-y-8">
          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/20 to-blue-600/20 rounded-xl blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div className="relative bg-white rounded-xl p-6 border border-gray-200 hover:border-emerald-300 transition-all duration-300 hover:shadow-lg">
              <div className="space-y-4">
                <label
                  htmlFor="file-upload"
                  className="block text-sm font-semibold text-gray-700 mb-3"
                >
                  <span className="flex items-center gap-2">
                    Upload Meeting Recording
                  </span>
                </label>
                <div className="relative border-2 border-dashed border-gray-300 rounded-lg hover:border-emerald-500 hover:bg-emerald-50/50 transition-all duration-200 group/upload">
                  <input
                    id="file-upload"
                    type="file"
                    className="absolute top-0 left-0 w-full h-full opacity-0 cursor-pointer"
                    accept=".mp3,.wav,.mp4,.m4a,.webm"
                    onChange={handleFileSelect}
                  />
                  <div className="py-8 text-center">
                    <div className="w-12 h-12 bg-gradient-to-r from-emerald-500 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 group-hover/upload:scale-110 transition-transform duration-200">
                      <svg
                        className="w-6 h-6 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                        />
                      </svg>
                    </div>
                    <span className="text-gray-900 font-medium">
                      {selectedFile
                        ? selectedFile.name
                        : "Click or drag file to upload"}
                    </span>
                    <p className="mt-2 text-sm text-gray-600">
                      Choose your meeting recording file
                    </p>
                    <p className="mt-1 text-xs text-gray-500">
                      Supported formats: mp3, wav, mp4, m4a, webm
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-600/20 rounded-xl blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <div className="relative bg-white rounded-xl p-6 border border-gray-200 hover:border-blue-300 transition-all duration-300 hover:shadow-lg">
                <label
                  htmlFor="project-key"
                  className="block text-sm font-semibold text-gray-700 mb-3"
                >
                  <span className="flex items-center gap-2">
                    Jira Project Key
                    <span className="text-red-500">*</span>
                  </span>
                </label>
                <input
                  type="text"
                  id="project-key"
                  value={projectKey}
                  onChange={(e) => setProjectKey(e.target.value)}
                  className="w-full px-4 py-3 text-gray-900 placeholder-gray-400 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all duration-200 outline-none hover:border-gray-300"
                  placeholder="e.g., PROJ, DEV, MAIN"
                />
                <p className="mt-2 text-xs text-gray-500">
                  The unique identifier for your Jira project
                </p>
              </div>
            </div>

            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-pink-600/20 rounded-xl blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <div className="relative bg-white rounded-xl p-6 border border-gray-200 hover:border-purple-300 transition-all duration-300 hover:shadow-lg">
                <label
                  htmlFor="assignee"
                  className="block text-sm font-semibold text-gray-700 mb-3"
                >
                  <span className="flex items-center gap-2">
                    Assignee (Optional)
                  </span>
                </label>
                <input
                  type="text"
                  id="assignee"
                  value={assignee}
                  onChange={(e) => setAssignee(e.target.value)}
                  className="w-full px-4 py-3 text-gray-900 placeholder-gray-400 border-2 border-gray-200 rounded-lg focus:border-purple-500 focus:ring-4 focus:ring-purple-100 transition-all duration-200 outline-none hover:border-gray-300"
                  placeholder="Jira username"
                />
                <p className="mt-2 text-xs text-gray-500">
                  Leave empty to assign automatically
                </p>
              </div>
            </div>
          </div>

          <div className="relative group mt-8">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl blur opacity-25 group-hover:opacity-40 transition-opacity duration-300"></div>
            <button
              onClick={handleUpload}
              disabled={isProcessing}
              className="relative w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-blue-100 hover:shadow-lg transform hover:-translate-y-0.5 disabled:hover:transform-none disabled:cursor-not-allowed"
            >
              <span className="flex items-center justify-center gap-2">
                {isProcessing ? (
                  <>
                    <svg
                      className="w-5 h-5 animate-spin"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                      />
                    </svg>
                    Processing...
                  </>
                ) : (
                  <>
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    Convert to Jira Tickets
                  </>
                )}
              </span>
            </button>
          </div>

          {isProcessing && (
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-purple-600/10 rounded-xl blur-sm opacity-100 transition-opacity duration-300"></div>
              <div className="relative bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-200">
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                    <svg
                      className="w-5 h-5 text-white animate-spin"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                      />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800">
                      Processing Your Meeting
                    </h3>
                    <p className="text-sm text-gray-600">
                      {status.message ||
                        "Analyzing audio and extracting tasks..."}
                    </p>
                  </div>
                </div>
                <div className="relative">
                  <div className="overflow-hidden h-3 rounded-full bg-gradient-to-r from-blue-200 to-purple-200">
                    <div
                      style={{ width: `${progress}%` }}
                      className="h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-full transition-all duration-500 ease-out"
                    ></div>
                  </div>
                  <div className="flex justify-between text-xs text-gray-500 mt-2">
                    <span>Progress</span>
                    <span>{progress}%</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {!isProcessing && status.message && (
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/10 to-blue-600/10 rounded-xl blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <div
                className={`relative border-2 rounded-xl p-6 ${
                  statusStyles?.[status.type] || statusStyles.info
                }`}
              >
                <div className="flex items-center gap-3">
                  {status.type === "success" && (
                    <div className="w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center">
                      <svg
                        className="w-5 h-5 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                    </div>
                  )}
                  {status.type === "error" && (
                    <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
                      <svg
                        className="w-5 h-5 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M6 18L18 6M6 6l12 12"
                        />
                      </svg>
                    </div>
                  )}
                  {status.type === "info" && (
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                      <svg
                        className="w-5 h-5 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                    </div>
                  )}
                  <p className="text-sm font-medium">{status.message}</p>
                </div>
              </div>
            </div>
          )}

          {tickets.length > 0 && (
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/10 to-blue-600/10 rounded-xl blur-sm opacity-100 transition-opacity duration-300"></div>
              <div className="relative bg-gradient-to-r from-emerald-50 to-blue-50 rounded-xl p-8 border border-emerald-200">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-12 h-12 bg-gradient-to-r from-emerald-500 to-blue-600 rounded-full flex items-center justify-center">
                    <svg
                      className="w-6 h-6 text-white"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-800">
                      Generated Jira Tickets
                    </h2>
                    <p className="text-gray-600">
                      {tickets.length} ticket{tickets.length !== 1 ? "s" : ""}{" "}
                      created successfully
                    </p>
                  </div>
                </div>
                <div className="space-y-4">
                  {tickets.map((ticket, index) => (
                    <div
                      key={ticket.key}
                      className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md transition-all duration-200 hover:border-blue-300"
                    >
                      <div className="flex justify-between items-start gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-3">
                            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-blue-100 text-blue-800">
                              {ticket.key}
                            </span>
                            <span className="text-sm text-gray-500">
                              #{index + 1}
                            </span>
                          </div>
                          <h3 className="text-lg font-semibold text-gray-800 mb-2">
                            {ticket.summary}
                          </h3>
                          {ticket.description && (
                            <p className="text-gray-600 text-sm line-clamp-2">
                              {ticket.description}
                            </p>
                          )}
                        </div>
                        <a
                          href={ticket.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium rounded-lg transition-colors duration-200"
                        >
                          <svg
                            className="w-4 h-4"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                            />
                          </svg>
                          View in Jira
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
