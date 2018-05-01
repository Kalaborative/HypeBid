var timer = new Timer();
$(document).ready( function () {
    timer.start({countdown: true, startValues: {seconds: 240}});
    $('#countdownExample .values').html(timer.getTimeValues().toString());
    timer.addEventListener('secondsUpdated', function (e) {
        $('#countdownStopwatch').html(timer.getTimeValues().toString());
    });
    timer.addEventListener('targetAchieved', function (e) {
        $('#countdownStopwatch').html('KABOOM!!');
    });
});