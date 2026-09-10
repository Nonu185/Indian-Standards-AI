async function testEndpoint() {
  const requirementText = "I need Ordinary Portland Cement Grade 43 for construction of a government building.";
  console.log(`Sending requirement to Express /api/recommendations:\n"${requirementText}"\n`);
  
  try {
    const response = await fetch('http://localhost:5001/api/recommendations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ requirement: requirementText }),
    });
    
    if (!response.ok) {
      console.error(`Express responded with status: ${response.status}`);
      const errorData = await response.json();
      console.error('Error:', errorData);
      return;
    }
    
    const data = await response.json();
    console.log("=== Response Received Successfully ===");
    console.log(JSON.stringify(data, null, 2));
  } catch (error) {
    console.error("Test failed:", error.message);
  }
}

testEndpoint();
