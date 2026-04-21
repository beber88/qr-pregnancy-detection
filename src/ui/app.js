/**
 * Pregnancy Detection AI — Frontend
 * Vanilla JS, no frameworks.
 * Research use only. Experimental probability model. Not a diagnostic test.
 */

(function () {
    "use strict";

    var dropZone = document.getElementById("dropZone");
    var fileInput = document.getElementById("fileInput");
    var fileName = document.getElementById("fileName");
    var previewContainer = document.getElementById("previewContainer");
    var previewImage = document.getElementById("previewImage");
    var analyzeBtn = document.getElementById("analyzeBtn");
    var resultCard = document.getElementById("resultCard");
    var resultStatus = document.getElementById("resultStatus");
    var awaitingMessage = document.getElementById("awaitingMessage");
    var gaugeContainer = document.getElementById("gaugeContainer");
    var gaugeArc = document.getElementById("gaugeArc");
    var gaugeValue = document.getElementById("gaugeValue");
    var validationSection = document.getElementById("validationSection");
    var validationList = document.getElementById("validationList");
    var featuresToggle = document.getElementById("featuresToggle");
    var featuresTable = document.getElementById("featuresTable");
    var featuresBody = document.getElementById("featuresBody");

    var selectedFile = null;

    // --- Drop zone events ---
    dropZone.addEventListener("click", function () {
        fileInput.click();
    });

    dropZone.addEventListener("dragover", function (e) {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });

    dropZone.addEventListener("dragleave", function () {
        dropZone.classList.remove("dragover");
    });

    dropZone.addEventListener("drop", function (e) {
        e.preventDefault();
        dropZone.classList.remove("dragover");
        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener("change", function () {
        if (fileInput.files.length > 0) {
            handleFile(fileInput.files[0]);
        }
    });

    function handleFile(file) {
        // Validate file type
        var validTypes = ["image/jpeg", "image/png", "image/jpg"];
        if (validTypes.indexOf(file.type) === -1) {
            alert("Please select a JPG or PNG image.");
            return;
        }

        selectedFile = file;
        fileName.textContent = file.name;
        dropZone.classList.add("has-file");
        analyzeBtn.disabled = false;

        // Show preview
        var reader = new FileReader();
        reader.onload = function (e) {
            previewImage.src = e.target.result;
            previewContainer.style.display = "block";
        };
        reader.readAsDataURL(file);

        // Hide previous results
        resultCard.classList.remove("visible");
    }

    // --- Analyze button ---
    analyzeBtn.addEventListener("click", function () {
        if (!selectedFile) return;

        analyzeBtn.disabled = true;
        analyzeBtn.classList.add("loading");
        analyzeBtn.textContent = "Analyzing...";
        resultCard.classList.remove("visible");

        var formData = new FormData();
        formData.append("file", selectedFile);

        fetch("/predict", {
            method: "POST",
            body: formData,
        })
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                showResult(data);
            })
            .catch(function (error) {
                showError("Connection error: " + error.message);
            })
            .finally(function () {
                analyzeBtn.disabled = false;
                analyzeBtn.classList.remove("loading");
                analyzeBtn.textContent = "Analyze Sample";
            });
    });

    // --- Display result ---
    function showResult(data) {
        resultCard.classList.add("visible");
        awaitingMessage.style.display = "none";
        gaugeContainer.style.display = "none";

        // Status
        if (data.status === "model_not_available") {
            resultStatus.textContent = "Model Not Yet Available";
            resultStatus.className = "result-status model-unavailable";
            awaitingMessage.style.display = "block";
        } else if (data.status === "success" && data.probability !== null) {
            resultStatus.textContent = "Analysis Complete";
            resultStatus.className = "result-status success";
            showGauge(data.probability);
        } else if (data.status === "validation_failed") {
            resultStatus.textContent = "Image Validation Failed";
            resultStatus.className = "result-status error";
        } else {
            resultStatus.textContent = data.error || "Unknown Status";
            resultStatus.className = "result-status error";
        }

        // Validation
        showValidation(data.validation);

        // Features
        showFeatures(data.features);
    }

    function showError(message) {
        resultCard.classList.add("visible");
        awaitingMessage.style.display = "none";
        gaugeContainer.style.display = "none";
        resultStatus.textContent = message;
        resultStatus.className = "result-status error";
        validationList.innerHTML = "";
        featuresBody.innerHTML = "";
        featuresTable.classList.remove("visible");
    }

    function showGauge(probability) {
        gaugeContainer.style.display = "block";
        var pct = Math.round(probability * 100);
        gaugeValue.textContent = pct + "%";

        // Arc: 251 is approximate total dash length for the semicircle
        var dashLen = (probability * 251).toFixed(1);
        gaugeArc.setAttribute("stroke-dasharray", dashLen + " 251");

        // Color based on probability
        var color;
        if (pct < 30) color = "#28a745";
        else if (pct < 70) color = "#ffc107";
        else color = "#dc3545";
        gaugeArc.setAttribute("stroke", color);
    }

    function showValidation(validation) {
        validationList.innerHTML = "";
        if (!validation) {
            validationSection.style.display = "none";
            return;
        }
        validationSection.style.display = "block";

        if (validation.is_valid) {
            addValidationItem("check", "Image passed all validation checks");
        }

        if (validation.issues) {
            validation.issues.forEach(function (issue) {
                addValidationItem("fail", issue);
            });
        }

        if (validation.warnings) {
            validation.warnings.forEach(function (warn) {
                addValidationItem("warn", warn);
            });
        }

        if (validation.metadata) {
            var meta = validation.metadata;
            if (meta.width && meta.height) {
                addValidationItem("check", "Dimensions: " + meta.width + "x" + meta.height + " px");
            }
            if (meta.mean_brightness !== undefined) {
                addValidationItem("check", "Brightness: " + meta.mean_brightness);
            }
            if (meta.laplacian_variance !== undefined) {
                addValidationItem("check", "Sharpness: " + meta.laplacian_variance);
            }
        }
    }

    function addValidationItem(type, text) {
        var div = document.createElement("div");
        div.className = "validation-item";

        var icon = document.createElement("span");
        icon.className = type;
        if (type === "check") icon.textContent = "\u2714";
        else if (type === "warn") icon.textContent = "\u26A0";
        else icon.textContent = "\u2718";

        var span = document.createElement("span");
        span.textContent = text;

        div.appendChild(icon);
        div.appendChild(span);
        validationList.appendChild(div);
    }

    function showFeatures(features) {
        featuresBody.innerHTML = "";
        featuresTable.classList.remove("visible");

        if (!features) {
            featuresToggle.style.display = "none";
            return;
        }

        featuresToggle.style.display = "block";

        var keys = Object.keys(features);
        keys.forEach(function (key) {
            var tr = document.createElement("tr");
            var tdName = document.createElement("td");
            tdName.textContent = key;
            var tdVal = document.createElement("td");
            var val = features[key];
            tdVal.textContent = typeof val === "number" ? val.toFixed(4) : val;
            tr.appendChild(tdName);
            tr.appendChild(tdVal);
            featuresBody.appendChild(tr);
        });
    }

    featuresToggle.addEventListener("click", function () {
        var isVisible = featuresTable.classList.contains("visible");
        featuresTable.classList.toggle("visible");
        featuresToggle.textContent = isVisible
            ? "Show extracted features"
            : "Hide extracted features";
    });
})();
