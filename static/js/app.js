const BASE_URL = "http://127.0.0.1:5000";

// Fetch locations
function fetchLocations() {
    fetch(`${BASE_URL}/get_location_names`)
        .then(response => response.json())
        .then(data => {
            console.log("Locations data received:", data);
            if (data.locations) {
                populateLocationsDropdown(data.locations);
            }
        })
        .catch(error => {
            console.error("Error fetching locations:", error);
        });
}

// Predict home price
function predictHomePrice(requestData) {
    fetch(`${BASE_URL}/predict_home_price`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(requestData)
    })
        .then(response => response.json())
        .then(data => {
            console.log("Prediction response:", data);
            if (data.estimated_price) {
                displayEstimatedPrice(data.estimated_price);
            } else {
                alert("Error: Unable to calculate price.");
            }
        })
        .catch(error => {
            console.error("Error predicting price:", error);
        });
}

// Populate locations dropdown
function populateLocationsDropdown(locations) {
    const locationsSelect = document.getElementById("uiLocations");
    locationsSelect.innerHTML = ""; // Clear existing options

    // Add a default option
    const defaultOption = document.createElement("option");
    defaultOption.text = "Select Location";
    defaultOption.value = "";
    defaultOption.disabled = true;
    defaultOption.selected = true;
    locationsSelect.appendChild(defaultOption);

    // Add locations to the dropdown
    locations.forEach(location => {
        const option = document.createElement("option");
        option.text = location;
        option.value = location;
        locationsSelect.appendChild(option);
    });
}

// Display the estimated price
function displayEstimatedPrice(price) {
    const priceDiv = document.getElementById("uiEstimatedPrice");
    const priceValue = document.getElementById("priceValue");

    priceDiv.style.display = "block";
    priceValue.textContent = `₹${price.toLocaleString("en-IN")}`;
}

// Example usage
document.addEventListener("DOMContentLoaded", function () {
    // Fetch locations on page load
    fetchLocations();

    // Attach event listener to the "Estimate Price" button
    document.getElementById("estimatePriceButton").addEventListener("click", function () {
        const sqft = document.getElementById("uiSqft").value;
        const bhk = document.querySelector('input[name="uiBHK"]:checked')?.value;
        const bath = document.querySelector('input[name="uiBathrooms"]:checked')?.value;
        const location = document.getElementById("uiLocations").value;

        // Input validation
        if (!sqft || parseFloat(sqft) <= 0) {
            alert("Please enter a valid square feet area.");
            return;
        }
        if (!bhk) {
            alert("Please select the number of bedrooms (BHK).");
            return;
        }
        if (!bath) {
            alert("Please select the number of bathrooms.");
            return;
        }
        if (!location) {
            alert("Please select a location.");
            return;
        }

        // Prepare request data
        const requestData = {
            total_sqft: parseFloat(sqft),
            bhk: parseInt(bhk),
            bath: parseInt(bath),
            location: location
        };

        // Predict home price
        predictHomePrice(requestData);
    });
});