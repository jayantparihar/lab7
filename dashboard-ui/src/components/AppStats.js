import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://acit3855.westus3.cloudapp.azure.com/processing/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Ph Level</th>
							<th>Chlorine Level</th>
						</tr>
						<tr>
							<td># PH: {stats['num_phlevel_reading']}</td>
							<td># Ch: {stats['num_chlorine_level']}</td>
						</tr>
						<tr>
							<td colSpan="2">Max Ph level: {stats['max_phlevel_reading']}</td>
						</tr>
						<tr>
							<td colSpan="2">Max Chlorine level: {stats['max_chlorine_level']}</td>
						</tr>
						<tr>
							<td colSpan="2">Max Water: {stats['max_water_level']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}
