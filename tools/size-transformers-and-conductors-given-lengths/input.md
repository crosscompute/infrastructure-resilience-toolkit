# Size Transformers and Conductors Given Lengths

Size transformers and conductors from service drop line lengths using customizable tables of transformer types and conductor types. Run a system wide check by specifying service drops connected to different transformers.

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

{ BUTTON_PANEL }

## Acknowledgments

Thanks to [Gustavo Cifuentes](https://www.linkedin.com/in/gcifuentes), [Marla J. Smith](https://www.linkedin.com/in/marla-smith-) and [Travis Weaver](https://www.linkedin.com/in/travisweaver) of [Withlacoochee River Electric Cooperative](https://wrec.net) for advice and feedback.

This tool uses the 1990 IEEE Standard 241 Page 72 formula for voltage drop.
