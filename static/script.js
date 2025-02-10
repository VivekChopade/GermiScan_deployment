function runCommand(commandType) {
    let data = { command: commandType };

    if (commandType === "video") {
        let videoName = prompt("Enter the video file Path:");
        if (!videoName) return;
        data.video_name = videoName;
    }
    if (commandType === "image") {
        let imageName = prompt("Enter the image file Path:");
        if (!imageName) return;
        data.image_name = imageName;
    }

    fetch("/run_yolo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => alert(result.message))
    .catch(error => console.error("Error:", error));
}






// Replace with your Google Search Engine ID
const googleSearchEngineId = '54f288f6c8a044c67';

// Replace with your Google API Key
const googleApiKey = 'AIzaSyBTfMKuTJE-rN-wGQMB-jtiMv2OlAM1KWM';

// Google Search Results Container
const googleSearchResults = document.getElementById('googleSearchResults');
const searchInput = document.getElementById('searchInput');
const searchButton = document.getElementById('searchButton');

// Function to perform Google search
function performGoogleSearch(query) {
    if (!query.trim()) {
        googleSearchResults.style.display = 'none';
        return;
    }

    const url = `https://www.googleapis.com/customsearch/v1?q=${encodeURIComponent(query)}&cx=${googleSearchEngineId}&key=${googleApiKey}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            displayGoogleResults(data.items || []);
        })
        .catch(error => {
            console.error('Error fetching search results:', error);
            googleSearchResults.innerHTML = '<div class="gsc-result">Error loading search results.</div>';
        });
}

// Function to display Google search results
function displayGoogleResults(results) {
    if (results.length === 0) {
        googleSearchResults.innerHTML = '<div class="gsc-result">No results found.</div>';
    } else {
        googleSearchResults.innerHTML = results.map(result => `
            <div class="gsc-result">
                <a href="${result.link}" target="_blank">${result.title}</a>
                <p>${result.snippet}</p>
            </div>
        `).join('');
    }
    googleSearchResults.style.display = 'block';
}

// Event listeners
searchButton.addEventListener('click', () => performGoogleSearch(searchInput.value));
searchInput.addEventListener('input', () => performGoogleSearch(searchInput.value));
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') performGoogleSearch(searchInput.value);
});

// Close results when clicking outside
document.addEventListener('click', (e) => {
    if (!searchContainer.contains(e.target)) {
        googleSearchResults.style.display = 'none';
    }
});



document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("searchInput");
    const searchResults = document.getElementById("googleSearchResults");

    // Show results when clicking on the input
    searchInput.addEventListener("focus", function () {
        if (searchInput.value.trim() !== "") {
            searchResults.style.display = "block";
        }
    });

    // Hide results when clicking outside the search container
    document.addEventListener("click", function (event) {
        if (!searchInput.contains(event.target) && !searchResults.contains(event.target)) {
            searchResults.style.display = "none";
        }
    });

    // Hide results when input is empty
    searchInput.addEventListener("input", function () {
        if (searchInput.value.trim() === "") {
            searchResults.style.display = "none";
        } else {
            searchResults.style.display = "block";
        }
    });
});