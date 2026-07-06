<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Log all request information
error_log("Request Method: " . $_SERVER['REQUEST_METHOD']);
error_log("Request URI: " . $_SERVER['REQUEST_URI']);
error_log("POST data: " . print_r($_POST, true));
error_log("FILES data: " . print_r($_FILES, true));

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $category = basename($_POST['category']); 
    error_log("Category: " . $category);
    
    $target_dir = "/var/www/html/uo_copilot/files/" . $category . "/files/";
    $target_file = $target_dir . basename($_FILES["file"]["name"]);
    
    error_log("Target dir: " . $target_dir);
    error_log("Target file: " . $target_file);
    
    $allowed_categories = array("animal", "bardic", "combat", "crafting", "looting", "resource");
    if (!in_array($category, $allowed_categories)) {
        error_log("Invalid category: " . $category);
        die("Invalid category");
    }
    
    if (move_uploaded_file($_FILES["file"]["tmp_name"], $target_file)) {
        error_log("File successfully uploaded to: " . $target_file);
        header("Location: " . $category);
    } else {
        error_log("Failed to move uploaded file");
        error_log("Upload error code: " . $_FILES["file"]["error"]);
        echo "Sorry, there was an error uploading your file.";
    }
} else {
    error_log("Invalid request method: " . $_SERVER['REQUEST_METHOD']);
    die("Invalid request method");
}
?>