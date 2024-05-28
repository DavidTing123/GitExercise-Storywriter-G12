function convertMarkdownToHtml() {
    // Get the Markdown input value
    const markdownInput = document.getElementById('content').value;
    
    // Function to replace Markdown syntax with HTML
    function markdownToHtml(markdown) {
        let html = markdown;
        
        // Replace headers (e.g., # Heading) with <h1>, <h2>, etc.
        html = html.replace(/^#\s+(.*)$/gm, '<h1>$1</h1>');
        html = html.replace(/^##\s+(.*)$/gm, '<h2>$1</h2>');
        html = html.replace(/^###\s+(.*)$/gm, '<h3>$1</h3>');
        html = html.replace(/^####\s+(.*)$/gm, '<h4>$1</h4>');
        html = html.replace(/^#####\s+(.*)$/gm, '<h5>$1</h5>');
        html = html.replace(/^######\s+(.*)$/gm, '<h6>$1</h6>');
        
        // Replace bold and italic
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Replace links
        html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
        
        // Replace unordered lists - tested NOT working # TZX006
        html = html.replace(/^\s*\*\s+(.*)$/gm, '<ul><li>$1</li></ul>');

        // Replace ordered lists - tested NOT working # TZX006
        html = html.replace(/^\s*1\.?\s+(.*)$/gm, '<ol><li>$1</li></ol>');

        // Replace line breaks - tested NOT working # TZX006
        html = html.replace(/  \n/g, '<br>');
        
        // Replace paragraphs
        html = `<p>${html.replace(/\n\n/g, '</p><p>')}</p>`;

        // Add rule for images (e.g., !Alt Text) - Not sure working or not !!!
        html = html.replace(/!\[([^\]]+)\]\(([^)]+)\)/g, '<img src="$2" alt="$1">');

        // Replace newline characters ('\n') with <br> tags.       TZX006
        html = html.replace(/\\n/g, '<br>');                     // TZX006

        // Replace the Markdown horizontal rule '---' with an HTML <hr> tag.       TZX006
        html = html.replace(/^---$/gm, '<hr>');                                 // TZX006
            
        return html;
    }
    
    // Convert Markdown to HTML
    const html = markdownToHtml(markdownInput);
    
    // Display the HTML output in the HTML output area
    const htmlOutput = document.getElementById('html-output');
    htmlOutput.innerHTML = html;
}
