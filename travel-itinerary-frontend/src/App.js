import React, { useState } from "react";

function App() {
    const [place, setPlace] = useState("");
    const [startDate, setStartDate] = useState("");
    const [endDate, setEndDate] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const response = await fetch("http://localhost:5000/download-pdf", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ place, start_date: startDate, end_date: endDate }),
            });
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "itinerary.pdf";
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
            } else {
                alert("Failed to generate PDF");
            }
        } catch (err) {
            alert("Error connecting to backend.");
        }
        setLoading(false);
    };

    return (
        <div style={{ maxWidth: 400, margin: "auto", padding: 20, fontFamily: "sans-serif" }}>
            <h2>Travel Itinerary Planner</h2>
            <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                <div>
                    <label>Place to Visit:</label>
                    <input
                        value={place}
                        onChange={e => setPlace(e.target.value)}
                        required
                        style={{ width: "100%", padding: 6, marginTop: 4 }}
                        placeholder="e.g. Mumbai"
                    />
                </div>
                <div>
                    <label>Start Date:</label>
                    <input
                        type="date"
                        value={startDate}
                        onChange={e => setStartDate(e.target.value)}
                        required
                        style={{ width: "100%", padding: 6, marginTop: 4 }}
                    />
                </div>
                <div>
                    <label>End Date:</label>
                    <input
                        type="date"
                        value={endDate}
                        onChange={e => setEndDate(e.target.value)}
                        required
                        style={{ width: "100%", padding: 6, marginTop: 4 }}
                    />
                </div>
                <button type="submit" disabled={loading}>
                    {loading ? "Generating PDF..." : "Download Itinerary"}
                </button>
            </form>
        </div>
    );
}

export default App;