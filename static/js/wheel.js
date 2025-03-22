document.addEventListener('DOMContentLoaded', function() {
    const wheel = document.getElementById('wheel');
    const spinButton = document.getElementById('spinButton');
    const canvas = document.getElementById('wheelCanvas');
    const ctx = canvas.getContext('2d');
    
    // Set canvas dimensions
    canvas.width = 400;
    canvas.height = 400;
    
    // Define wheel segments
    const segments = [
        { text: '100', color: '#4CAF50', value: 100 },
        { text: '200', color: '#2196F3', value: 200 },
        { text: '300', color: '#FFC107', value: 300 },
        { text: '400', color: '#9C27B0', value: 400 },
        { text: '500', color: '#E91E63', value: 500 },
        { text: '600', color: '#FF5722', value: 600 },
        { text: '700', color: '#795548', value: 700 },
        { text: '800', color: '#607D8B', value: 800 },
        { text: '900', color: '#3F51B5', value: 900 },
        { text: '1000', color: '#8BC34A', value: 1000 },
        { text: 'MẤT ĐIỂM', color: '#F44336', value: 'bankrupt' }
    ];
    
    const numSegments = segments.length;
    const segmentAngle = (2 * Math.PI) / numSegments;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) - 10;
    
    let isSpinning = false;
    let spinAngle = 0;
    let spinVelocity = 0;
    let selectedSegment = null;
    
    // Draw the wheel
    function drawWheel() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw wheel segments
        for (let i = 0; i < numSegments; i++) {
            const segment = segments[i];
            const startAngle = i * segmentAngle + spinAngle;
            const endAngle = (i + 1) * segmentAngle + spinAngle;
            
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, startAngle, endAngle);
            ctx.closePath();
            
            ctx.fillStyle = segment.color;
            ctx.fill();
            ctx.strokeStyle = '#333';
            ctx.lineWidth = 2;
            ctx.stroke();
            
            // Draw text
            ctx.save();
            ctx.translate(centerX, centerY);
            ctx.rotate(startAngle + segmentAngle / 2);
            ctx.textAlign = 'right';
            ctx.fillStyle = '#fff';
            ctx.font = 'bold 16px Arial';
            ctx.fillText(segment.text, radius - 20, 5);
            ctx.restore();
        }
        
        // Draw center circle
        ctx.beginPath();
        ctx.arc(centerX, centerY, 20, 0, 2 * Math.PI);
        ctx.fillStyle = '#333';
        ctx.fill();
        
        // Draw pointer
        ctx.beginPath();
        ctx.moveTo(centerX + radius + 10, centerY);
        ctx.lineTo(centerX + radius - 10, centerY - 15);
        ctx.lineTo(centerX + radius - 10, centerY + 15);
        ctx.closePath();
        ctx.fillStyle = '#e91e63';
        ctx.fill();
    }
    
    // Animate the wheel spin
    function animateWheel() {
        spinAngle += spinVelocity;
        spinVelocity *= 0.99; // Apply friction
        
        drawWheel();
        
        if (spinVelocity > 0.001) {
            requestAnimationFrame(animateWheel);
        } else {
            isSpinning = false;
            spinButton.disabled = false;
            determineWinner();
        }
    }
    
    // Determine which segment is selected
    function determineWinner() {
        // Calculate the position of the pointer relative to the wheel
        const pointerAngle = Math.PI / 2; // The pointer is at the top
        
        // Calculate which segment is at the pointer
        let normalizedAngle = (spinAngle % (2 * Math.PI));
        if (normalizedAngle < 0) normalizedAngle += 2 * Math.PI;
        
        // Find which segment is at the pointer
        const winningSegmentIndex = numSegments - 1 - Math.floor(((normalizedAngle + pointerAngle) % (2 * Math.PI)) / segmentAngle);
        const winningSegment = segments[winningSegmentIndex % numSegments];
        
        selectedSegment = winningSegment;
        
        // Call the handler function in script.js
        window.handleSpin(winningSegment.value);
    }
    
    // Spin the wheel when button is clicked
    spinButton.addEventListener('click', function() {
        if (!isSpinning) {
            isSpinning = true;
            spinButton.disabled = true;
            spinVelocity = 0.2 + Math.random() * 0.2; // Random spin speed
            animateWheel();
        }
    });
    
    // Initial wheel draw
    drawWheel();
});
