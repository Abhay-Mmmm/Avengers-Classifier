Dropzone.autoDiscover = false;

function init() {
    let dz = new Dropzone("#dropzone", {
        url: "/",
        maxFiles: 1,
        addRemoveLinks: true,
        dictDefaultMessage: "Some Message",
        autoProcessQueue: false
    });
    
    dz.on("addedfile", function() {
        if (dz.files[1]!=null) {
            dz.removeFile(dz.files[0]);        
        }
    });

    dz.on("complete", function (file) {
        let imageData = file.dataURL;
        
        var url = "http://localhost:5000/classify_image";

        $.post(url, {
            image_data: file.dataURL
        },function(data, status) {
            console.log("Received data:", data);
            if (!data || data.length==0) {
                $("#resultHolder").hide();
                $("#divClassTable").hide();                
                $("#error").show();
                return;
            }
            let players = ["bruce_banner", "clint_barton", "natasha_romanoff", "steve_rogers", "thor_odinson", "tony_stark"];
            
            let match = null;
            let bestScore = -1;
            for (let i=0;i<data.length;++i) {
                let maxScoreForThisClass = Math.max(...data[i].class_probability);
                if(maxScoreForThisClass>bestScore) {
                    match = data[i];
                    bestScore = maxScoreForThisClass;
                }
            }
            if (match) {
                $("#error").hide();
                $("#divClassTable").show();
                let personCard = $(`[data-player=\"${match.class}\"]`).html();
                let personDiv = `<div class='card border-0' style='display:inline-block;'>${personCard}</div>`;
                $("#classifiedPerson").html(personDiv);
                
                // Ensure the class dictionary is properly formatted
                let classDictionary = match.class_dictionary;
                console.log("Class dictionary:", classDictionary);
                
                // Update the table with probability scores
                for(let i=0; i<players.length; i++) {
                    let playerName = players[i];
                    let index = classDictionary[playerName];
                    let probabilityScore = 0;
                    
                    // Make sure we have a valid index and class_probability has enough elements
                    if (index !== undefined && 
                        match.class_probability && 
                        index < match.class_probability.length) {
                        probabilityScore = match.class_probability[index];
                    }
                    
                    let elementName = "#score_" + playerName;
                    $(elementName).html((probabilityScore * 100).toFixed(1) + '%');
                }
            }
            dz.removeFile(file);            
        });
    });

    $("#submitBtn").on('click', function (e) {
        dz.processQueue();		
    });
}

$(document).ready(function() {
    console.log( "ready!" );
    $("#error").hide();
    $("#resultHolder").hide();
    $("#divClassTable").hide();

    init();
});