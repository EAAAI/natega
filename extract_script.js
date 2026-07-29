const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);
if (scriptMatch) {
    const code = scriptMatch[1];
    fs.writeFileSync('temp_script.js', code);
    console.log("Script extracted.");
} else {
    console.log("No script found.");
}
