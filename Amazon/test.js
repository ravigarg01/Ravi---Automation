function searchType(val) {
    var indetityTypeId = document.getElementById('indentityTypeSelect').value
    var st = document.getElementById('st');
    var stl = document.getElementById('stl');
    var stDiv = document.getElementById('stDiv');
    var idewise = document.getElementById('idewise');
    var idewiseDiv = document.getElementById('idewiseDiv');
   
    switch (val) {

        case 'State Wise':
            {
                Get_TblMasterState('st');
                stl.innerHTML = 'State Wise';
                stDiv.removeAttribute('hidden');
                break;
            }
        case 'City Wise':
            {
                Get_TblMasterCity('st');
                stl.innerHTML = 'City Wise';
                stDiv.removeAttribute('hidden');
                break;
            }
        case 'University Wise':
            {
                Get_TblMasterUniversity('st');
                stl.innerHTML = 'University Wise';
                stDiv.removeAttribute('hidden');
                break;
            }
        case 'Identity Wise':
            {
                loader.initialize();
                loader.showLoader();
                Get_TblMasterIdentityName('st', University, indetityTypeId);
                stl.innerHTML = 'Identity Wise';
                stDiv.removeAttribute('hidden');
                break;
            }

        case 'Sales Member':
            {
                Get_TblMasterSalesMember('st');
                stl.innerHTML = 'Sales Member';
                stDiv.removeAttribute('hidden');
                break;
            }
        case 'null':
            {
                st.innerHTML = '';
                /*idewise.innerHTML = '';*/
                stDiv.setAttribute('hidden', 'true');
                /*idewiseDiv.setAttribute('hidden', 'true');*/
            }
    }
}


document.addEventListener("DOMContentLoaded", function (event) {

    GetUniversityDetails().then();

    async function GetUniversityDetails() {
        getFetch('/api/Master/Get_MasterUniversityDetails/' + _UniversityId, _Token).then((res) => {
            res = JSON.parse(res);
            var university = res[1][0]
            var state = res[1][1];
            var city = res[1][2]
            var salesmanager = res[1][3]
            var status = res[1][4];
            getFetch('/api/Identity/Get_TblMasterState', _Token).then((res) => {
                $.each(res, function (i) {
                    var opt = document.createElement('option');
                    opt.value = res[i].stateID;
                    opt.innerHTML = res[i].state;
                    document.getElementById('state').append(opt);
                });
            }).then((res) => {
                $('#state').selectpicker('refresh');
                document.getElementById('state').value = state;
                $('#state').selectpicker('refresh');
            });
            getFetch('/api/Identity/Get_TblMasterCityByState/' + state, _Token).then((res) => {
                $.each(res, function (i) {
                    var opt = document.createElement('option');
                    opt.value = res[i].cityID;
                    opt.innerHTML = res[i].city;
                    document.getElementById('city').append(opt);
                });
            }).then((res) => {

                $('#city').selectpicker('refresh');
                var select = document.getElementById('city');
                for (var i = 0, l = select.options.length, o; i < l; i++) {
                    o = select.options[i];
                    if (city.indexOf(o.value) != -1) {
                        o.selected = true;
                    }
                }

                $('#city').selectpicker('refresh');
            });
        });
    }
});  