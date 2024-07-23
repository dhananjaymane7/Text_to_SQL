const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const axios = require('axios'); // Import axios for HTTP requests

const app = express();
const port = 8000;

app.use(cors());
app.use(bodyParser.json());

app.post('/api/query', async (req, res) => {
  const { query } = req.body;

  // Fixed context value
  const context = "CREATE TABLE Persons (PersonID int, LastName varchar(255), FirstName varchar(255), Address varchar(255), City varchar(255));";

  try {
    // Forward the request to the external API with fixed context
    const response = await axios.post('http://213.180.0.67:20037/api/query', {
      query,
      context,
    });

    // Send the response back to the client
    res.json(response.data);
  } catch (error) {
    // Debugging information
    console.error('Error forwarding request:', error.response ? error.response.data : error.message);
    res.status(500).json({ error: 'An error occurred while processing your query.' });
  }
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
