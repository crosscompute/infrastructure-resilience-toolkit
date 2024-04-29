{ maximum_voltage_drop_percent }
{ temperature_in_celsius }
{ service_drops_text }

<a id="extra-button" class="link">Extra Settings</a>

<div id="extra-div" class="_template">
{ transformer_types_csv }
{ conductor_types_csv }
</div>

<script>
const extraButton = document.getElementById('extra-button');
const extraDiv = document.getElementById('extra-div');
extraButton.addEventListener('click', function() {
  extraButton.classList.add('hidden');
  extraDiv.style.display = 'flex';
});
</script>
